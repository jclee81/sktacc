pkill redis-server
cd ./redis-4.0.1/utils/create-cluster
./create-cluster stop
./create-cluster start
./create-cluster clean
./create-cluster create
