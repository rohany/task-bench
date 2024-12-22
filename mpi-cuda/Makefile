MPICXX ?= g++

DEBUG ?= 0

CXXFLAGS ?=
CXXFLAGS += -std=c++11 -I../core -DENABLE_CUDA -I$(CUDA_ROOT)/include/ -I/opt/conda/envs/legate/include -pthread -I/opt/conda/envs/legate/include

LDFLAGS ?=
LDFLAGS += -L../core -lcore_s -lcore_cuda_s -L$(CUDA_ROOT)/lib64/ -lcudart -pthread -I/opt/conda/envs/legate/include -L/opt/conda/envs/legate/lib -L/opt/conda/envs/legate/lib -Wl,-rpath,/opt/conda/envs/legate/lib -lmpi

ifeq ($(strip $(DEBUG)),0)
	CXXFLAGS += -O3
else
	CXXFLAGS += -O0 -ggdb
endif

include ../core/make_blas.mk

BIN := main

.PHONY: all
all:  $(BIN)

$(BIN): %:%.cc
	$(MPICXX) -o $@ $(CXXFLAGS) $< $(LDFLAGS)

.PHONY: clean
clean:
	rm -f *.o $(BIN)
