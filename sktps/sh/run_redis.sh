pkill redis-server
pushd ./redis-4.0.1/utils/create-cluster
# ./create-cluster create
./create-cluster stop
./create-cluster start
popd
./redis-4.0.1/src/redis-server
