import ray
import sys
import core
import time
import os
import cupy

# Every Ray task runs in a fresh process, meaning that I don't see an
# easy way to persist the GPU memory across tasks?
@ray.remote(num_gpus=1)
def execute_point(graph_array, timestep, point, scratch, *inputs):
    gpu = ray.get_gpu_ids()[0]
    # Unfortunately this will allocate data on every task, meaning there's
    # going to be some startup overhead.
    core.init_cuda_support(graph_array, gpu)
    return core.execute_point_impl(graph_array, timestep, point, scratch, gpu, *inputs)

# @ray.remote(num_gpus=1)
# def init_gpu(graph_array):
#     gpu = ray.get_gpu_ids()[0]
#     cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "Not set")
#     print(f"Running on CUDA_VISIBLE_DEVICES={cuda_visible}")
#     print("IN INIT GPU: ", gpu)
#     cupy.cuda.runtime.setDevice(gpu)
#     core.init_cuda_support(graph_array, gpu)

def execute_task_graph(graph):
    graph_array = core.encode_task_graph(graph)
    assert(graph.scratch_bytes_per_task == 0)
    # scratch = [
    #     core.init_scratch_delayed(graph.scratch_bytes_per_task)
    #     for _ in range(graph.max_width)
    # ]
    # else:
    #     assert(
    scratch = [None for _ in range(graph.max_width)]

    # TODO (rohany): Need to launch a bunch of tasks here to initialize the GPUs.
    # TODO (rohany): Are we just at the whim of the scheduler here? That seems unfortunate.

    # num_gpus = int(ray.cluster_resources()['GPU'])
    # for i in range(num_gpus):
    #     init_gpu.remote(graph_array)

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
            output = execute_point.remote(graph_array, timestep, point, scratch[point], *inputs)
            row.append(output)
            outputs.append(output)
        for point in range(offset + width, graph.max_width):
            row.append(None)
        assert len(row) == graph.max_width
        last_row = row
    return outputs

def execute_task_bench():
    app = core.app_create(sys.argv)
    task_graphs = core.app_task_graphs(app)
    start_time = time.perf_counter()
    results = []
    # TODO (rohany): Run it twice?
    for task_graph in task_graphs:
        results.extend(execute_task_graph(task_graph))
    ray.get(results)
    total_time = time.perf_counter() - start_time
    core.c.app_report_timing(app, total_time)

if __name__ == "__main__":
    # ray.init(address="auto")
    ray.init()
    execute_task_bench()
