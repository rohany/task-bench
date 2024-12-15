#ifndef CUDA_KERNEL_H
#define CUDA_KERNEL_H

// #include <cuda.h>
// #include <cuda_runtime.h>

#include <unordered_map>

extern std::unordered_map<uint64_t, char*> local_buffer;

struct Kernel;
struct TaskGraph;

// extern std::vector<char*> local_buffer;

extern size_t local_buffer_size;

// void init_cuda_support(const std::vector<TaskGraph> &graphs);
void init_cuda_support(const std::vector<TaskGraph> &graphs, uint64_t gpuid);

void fini_cuda_support();

void execute_kernel_compute_cuda(const Kernel &kernel, char *scratch_ptr, size_t scratch_bytes);

#endif
