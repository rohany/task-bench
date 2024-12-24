pushd eos_metg_compute

export STEPS=2000

./metg_mpi.sh
./metg_cuda.sh
./metg_cuda_graphs.sh
./metg_realm.sh
./metg_realm_staticsubgraph.sh

popd
