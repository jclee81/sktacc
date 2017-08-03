#!/usr/bin/python

from db_manager import DBManager
import json, os, sys
from optparse import OptionParser

HOST='localhost'
USER='tim_admin'
PW='niclab1234'

class TimAiExecutor:
    def __init__(self, db_inst):
        self._db_inst = db_inst

    def runTest(self):
        print "== Execute Query TEST =="
        test_query_1 = "select * from host"
        test_query_2 = "select * from lab where l_code = %s"
        self._db_inst.executeSQL(test_query_1)
        print self._db_inst.fetchAll()
        self._db_inst.executeSQLWithParams(test_query_2, ('HMI'))
        print self._db_inst.fetchAllWithParams()

    # RETURN : list of dictionary [{col_name:value},..]
    def getContainerInfo(self, u_id):
        self._db_inst.executeSQLWithParams(
                "select c_name,c_gpu_idxes,d_name,h_name, ports, extra_vols \
                from container where u_id=%s",(u_id))
        return self._db_inst.fetchAllWithParams()

    def getHostInfo(self, h_name):
        self._db_inst.executeSQLWithParams(
                "select h_ip, h_gpu_spec from host where h_name=%s",(h_name))
        return self._db_inst.fetchAllWithParams()

    def getDockerImageInfo(self, d_name):
        self._db_inst.executeSQLWithParams(
                "select d_dockerfile_path, d_start_command from docker_image where d_name=%s",(d_name))
        return self._db_inst.fetchAllWithParams()

    def getLabCode(self, u_id):
        self._db_inst.executeSQLWithParams(
                "select l_code from user where u_id=%s",(u_id))
        return self._db_inst.fetchAllWithParams()

    def getUser(self):
        self._db_inst.executeSQL(
                "select u_id from user")
        return self._db_inst.fetchAll()

class DockerRunCmdConstructor:
    def __init__(self, tae):
        self._tae = tae;

    def getDockerRunCmd(self, u_id):
        rows = self._tae.getContainerInfo(u_id)
        cmds=[]
        for row in rows:
            # ssh host
            cmd = "ssh %s" % (row['h_name'])
            # --name, --net
            cmd += " \"nvidia-docker run --name %s --net=host" % (row['c_name'])
            # -e
            ports = json.loads(row['ports'])
            for p in ports:
                cmd += " -e %s=%s" % (p, ports[p])
            # --device
            i = 0
            if row['c_gpu_idxes'] != "":
                for g in row['c_gpu_idxes'].split(','):
                    cmd += " --device /dev/nvidia%s:/dev/nvidia%s" % (g, i)
                    i += 1
                cmd += " --device /dev/nvidiactl:/dev/nvidiactl"
                cmd += " --device /dev/nvidia-uvm:/dev/nvidiactl-uvm"
            # -v
            lc = self._tae.getLabCode(u_id)
            cmd += " -v /etc/alternatives:/etc/alternatives-hadoop:ro"
            cmd += " -v /opt/cloudera:/opt/cloudera:ro"
            cmd += " -v /etc/hadoop/conf.cloudera.yarn:/etc/hadoop/conf:ro"
            for i in range(1,6):
                cmd += " -v /local%d:/local%d" % (i, i)
            cmd += " -v /hdfs:/hdfs"
#            cmd += " -v /data1:/data1"
            if lc[0]['l_code'] == "STL" or lc[0]['l_code'] == "NLP" or lc[0]['l_code'] == "KTL":
                cmd += " -v /nfs/user/TECH2:/nfs"
            else:
                cmd += " -v /nfs/user/%s:/nfs" % lc[0]['l_code']
            cmd += " -v /afnas_sata/%s:/afnas_sata" % lc[0]['l_code']
            if row['extra_vols'] is not None:
                extra_vols = json.loads(row['extra_vols'])
                for v in extra_vols:
                    cmd += " -v /afnas_sata/%s:/afnas_sata_share:%s" % (v, extra_vols[v])
            # --ulimit, -it -d
            cmd += " --ulimit nofile=65536:65536"
            cmd += " -it"
            cmd += " -d"
            # restart
            cmd += " --restart=always"
            # dockerfile_path, start_command
            dii = self._tae.getDockerImageInfo(row['d_name'])
            cmd += " %s" % (dii[0]['d_dockerfile_path'])
            cmd += " %s" % (dii[0]['d_start_command'])
            cmd += "\" &"

            cmds.append(cmd)
        return cmds

if __name__ == "__main__":
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--all", action="store_true", dest="all", help="all users", default=False)
    parser.add_option("-u", "--uid", dest="uid", help="specify a user", default="0000000")
    parser.add_option("-x", "--execute", action="store_true", dest="exe", help="execute docker run command", default=False)

    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        exit(1)
    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    print "Running TIM4AI..."
    db_inst = DBManager(HOST, USER, PW, 'tim_db', 'utf8')
    tae = TimAiExecutor(db_inst)
    drcc = DockerRunCmdConstructor(tae)

    if options.all:
        usrs = tae.getUser()
        for usr in usrs:
            print "User %s" % usr
            drcs = drcc.getDockerRunCmd(usr)
            print "    Number of containers to be run: %d" % len(drcs)
            print "    Commands:"
            for drc in drcs:
                print "        %s" % drc
                if options.exe:
                    os.system(drc)
    elif options.uid:
        drcs = drcc.getDockerRunCmd(options.uid)
        print "    Number of containers to be run: %d" % len(drcs)
        print "    Commands:"
        for drc in drcs:
            print "        %s" % drc
            if options.exe:
                os.system(drc)

