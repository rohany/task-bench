#!/bin/bash
export CUDA_VISIBLE_DEVICES=$OMPI_COMM_WORLD_LOCAL_RANK

# Use for profiling?
export PMIX_MCA_gds=hash
if [ $OMPI_COMM_WORLD_RANK -eq 1 ]; then
  nsys profile -t mpi,cuda,osrt "$@"
else
  "$@"
fi

$@
