pkill redis-server
cd ./redis-4.0.1/utils/create-cluster
# ./create-cluster create
./create-cluster stop
./create-cluster start
redis-server
