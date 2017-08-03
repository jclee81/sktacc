# parameter server daemon
from rediscluster import StrictRedisCluster

# this is test code
startup_nodes = [{"host": "127.0.0.1", "port": "30001"}]
rc = StrictRedisCluster(startup_nodes=startup_nodes,
                        decode_responses=True)
rc.set("foo", "bar")
print(rc.get("foo"))
