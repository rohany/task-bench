import ray
import ray.dag
import sys
import core
import time
import os
import cupy

@ray.remote(num_gpus=1.0 * float(os.environ.get('GPU_FRAC', 1.0)), num_cpus=1)
class GPU:
    def __init__(self, graph_array):
        core.init_cuda_support(graph_array, 0)

    def execute_point(self, graph_array, timestep, point, *inputs):
        return core.execute_point_impl(graph_array, timestep, point, None, 0, *inputs)


def execute_task_graph(graph, gpus):
    graph_array = core.encode_task_graph(graph)
    assert(graph.scratch_bytes_per_task == 0)

    outputs = []
    last_row = None
    for timestep in range(0, graph.timesteps):
        offset = core.c.task_graph_offset_at_timestep(graph, timestep)
        width = core.c.task_graph_width_at_timestep(graph, timestep)
        row = []
        for point in range(0, offset):
            row.append(None)
        for point in range(offset, offset + width):
            inputs = []
            for dep in core.task_graph_dependencies(graph, timestep, point):
                inputs.append(last_row[dep])
            points_per_proc = graph.max_width // len(gpus)
            output = gpus[point // points_per_proc].execute_point.remote(graph_array, timestep, point, *inputs)
            row.append(output)
            outputs.append(output)
        for point in range(offset + width, graph.max_width):
            row.append(None)
        assert len(row) == graph.max_width
        last_row = row
    return outputs

def execute_task_graph_compgraph(graph, gpus):
    graph_array = core.encode_task_graph(graph)
    assert(graph.scratch_bytes_per_task == 0)
    # assert(graph.timestep_period == 1)

    ray_graph = None
    previous_row = None
    start_time = None
    end_time = None

    # Execute the graph in batches of this size.
    batchsize = 25
    assert(graph.timesteps % batchsize == 0)
    for start_timestep in range(0, graph.timesteps, batchsize):
        # Always define the graph, and start timer only once the steady state is hit?
        # TODO (rohany): Gaurd condition for the dag definition
        if start_timestep == 0:
            last_row = None
            for timestep in range(start_timestep, start_timestep + batchsize):
                offset = core.c.task_graph_offset_at_timestep(graph, timestep)
                width = core.c.task_graph_width_at_timestep(graph, timestep)
                row = []
                for point in range(0, offset):
                    row.append(None)
                for point in range(offset, offset + width):
                    inputs = []
                    for dep in core.task_graph_dependencies(graph, timestep, point):
                        inputs.append(last_row[dep])
                    points_per_proc = graph.max_width // len(gpus)
                    output = gpus[point // points_per_proc].execute_point.remote(graph_array, timestep, point, *inputs)
                    row.append(output)
                for point in range(offset + width, graph.max_width):
                    row.append(None)
                assert len(row) == graph.max_width
                last_row = row
            previous_row = [ray.get(o) for o in last_row]
        else:
            if ray_graph is None:
                with ray.dag.InputNode() as inp:
                    last_row = inp
                    for timestep in range(start_timestep, start_timestep + batchsize):
                        offset = core.c.task_graph_offset_at_timestep(graph, timestep)
                        width = core.c.task_graph_width_at_timestep(graph, timestep)
                        row = []
                        for point in range(0, offset):
                            row.append(None)
                        for point in range(offset, offset + width):
                            inputs = []
                            for dep in core.task_graph_dependencies(graph, timestep, point):
                                inputs.append(last_row[dep])
                            points_per_proc = graph.max_width // len(gpus)
                            local_idx = timestep - start_timestep
                            output = gpus[point // points_per_proc].execute_point.bind(graph_array, inp[graph.max_width + local_idx], point, *inputs)
                            row.append(output)
                        for point in range(offset + width, graph.max_width):
                            row.append(None)
                        assert len(row) == graph.max_width
                        last_row = row
                ray_graph = ray.dag.MultiOutputNode(last_row).experimental_compile()
                start_time = time.perf_counter()
                # print("done compiling graph")
            args = previous_row + list(range(start_timestep, start_timestep + batchsize)) 
            # print(args)
            previous_row = ray.get(ray_graph.execute(*args))
            # print("done invoking graph")
    end_time = time.perf_counter()
    return end_time - start_time

def execute_task_bench():
    print("Running standard version!")
    app = core.app_create(sys.argv)
    task_graphs = core.app_task_graphs(app)
    assert(len(task_graphs) == 1)
    graph = task_graphs[0]
    assert(graph.scratch_bytes_per_task == 0)

    # Create all the GPUs.
    gpus = [GPU.remote(core.encode_task_graph(graph)) for _ in range(graph.max_width)]

    results = []
    for task_graph in task_graphs:
        results.extend(execute_task_graph(task_graph, gpus))
    ray.get(results)

    start_time = time.perf_counter()
    results = []
    for task_graph in task_graphs:
        results.extend(execute_task_graph(task_graph, gpus))
    ray.get(results)
    total_time = time.perf_counter() - start_time
    core.c.app_report_timing(app, total_time)

def execute_task_bench_graphs():
    print("Running cgraphs version!")
    app = core.app_create(sys.argv)
    task_graphs = core.app_task_graphs(app)
    assert(len(task_graphs) == 1)
    graph = task_graphs[0]
    assert(graph.scratch_bytes_per_task == 0)

    # Create all the GPUs.
    gpus = [GPU.remote(core.encode_task_graph(graph)) for _ in range(graph.max_width)]
    core.c.app_report_timing(app, execute_task_graph_compgraph(graph, gpus))

# TODO (rohany): Handle higher widths later...
@ray.remote(num_gpus=1)
class Worker:
    def __init__(self, graph_array, point, driver):
        self.graph = core.decode_task_graph(graph_array)
        self.graph_array = graph_array
        self.point = point
        assert(self.graph.scratch_bytes_per_task == 0)
        self.gpu = 0
        core.init_cuda_support(graph_array, 0)
        self.table = {}
        for i in range(self.graph.timesteps + 1):
            self.table[i] = {}
        self.driver = driver
        self.all_workers = None

    def start(self):
        self.all_workers = ray.get(self.driver.get_all_workers.remote())
        # Execute timestep 0?
        output = core.execute_point_impl(self.graph_array, 0, self.point, None, 0)
        for dep in core.task_graph_rev_dependencies(self.graph, 0, self.point):
            self.all_workers[dep].parent_finished.remote(0, self.point, output)

    def parent_finished(self, timestep, point, output):
        self.table[timestep + 1][point] = output
        self.handle_ready(timestep + 1)

    def handle_ready(self, timestep):
        ready_deps = self.table.get(timestep)
        inputs = []
        total = 0
        for dep in core.task_graph_dependencies(self.graph, timestep, self.point):
            total += 1
            data = ready_deps.get(dep, None)
            if data is not None:
                inputs.append(data)
        if len(inputs) == total:
            output = core.execute_point_impl(self.graph_array, timestep, self.point, None, 0, *inputs)
            if timestep != self.graph.timesteps - 1:
                for dep in core.task_graph_rev_dependencies(self.graph, timestep, self.point):
                    self.all_workers[dep].parent_finished.remote(timestep, self.point, output)
            else:
                self.driver.notify.remote()

@ray.remote
class Driver:
    def __init__(self, argv):
        self.app = core.app_create(argv)
        task_graphs = core.app_task_graphs(self.app)
        assert(len(task_graphs) == 1)
        self.graph = task_graphs[0]
        self.counter = self.graph.max_width
        self.done = False
        self.total_time = None

    def get_all_workers(self):
        return self.workers

    def start(self, dref):
        self.workers = [Worker.remote(core.encode_task_graph(self.graph), point, dref) for point in range(self.graph.max_width)]
        self.start_time = time.perf_counter()
        for w in self.workers:
            w.start.remote()

    def notify(self):
        self.counter -= 1
        assert(self.counter >= 0)
        if self.counter == 0:
            total_time = time.perf_counter() - self.start_time
            core.c.app_report_timing(self.app, total_time)
            sys.stdout.flush()
            sys.stderr.flush()
            self.done = True
            self.total_time = total_time

    def is_done(self):
        return self.done, self.total_time


# This version is more like the control replicated actors...
def execute_task_bench2():
    print("Running control replicated version!")
    d = Driver.remote(sys.argv)
    d.start.remote(d)
    while True:
        done, t = ray.get(d.is_done.remote())
        if done:
            app = core.app_create(sys.argv)
            core.c.app_report_timing(app, t)
            break
        time.sleep(1)

if __name__ == "__main__":
    ray.init()
    if 'cgraphs' in sys.argv:
        execute_task_bench_graphs()
    else:
        execute_task_bench()
