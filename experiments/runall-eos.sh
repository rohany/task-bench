pushd eos_metg_compute

export STEPS=2000

./metg_mpi.sh
./metg_realm.sh
./metg_realm_staticsubgraph.sh

popd
