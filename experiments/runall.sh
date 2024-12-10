pushd cori_metg_compute

VARIANT=nonblock ./metg_mpi.sh
./metg_realm.sh
./metg_realm_staticsubgraph.sh

popd
