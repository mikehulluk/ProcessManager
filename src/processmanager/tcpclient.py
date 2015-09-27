
# New structure - handle incoming socket requests manually:
import socket
import threading
import socketserver
import time

import json
import functools
from threading import Thread

import common

class ProcessMgrProcess(object):
    def __init__(self, process_name):
        self.process_name = process_name

class ProcessMgrIO(object):
    def __init__(self, process_mgr_name):
        self.process_mgr_name = process_mgr_name
        self.processes = []
    def add_process(self, process):
        self.processes.append(process)
    def register(self,):
        pass

import subprocess
from subprocess import Popen

def start_process_mgr(process_mgr_name):
    print ('Pretending to be client:Msg=%s' % process_mgr_name)


    ip, port = "localhost", common.Ports.ProcessMgrs
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    process_list = [
        ('process1', Popen('top', stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1 ), { 1:'stdout',2:'stderr'} ),
        ('process2', Popen('top', stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1 ), { 3:'stdout',4:'stderr'} ),
        ('process3', Popen('top', stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1 ), { 5:'stdout',6:'stderr'} ),
            ]
        
    msg = {'name':'MgrX','processes': [
        dict([ ('name',p0), ('outpipes',p2) ]) for (p0,p1,p2) in process_list] 
        }

#   msg = {'name':'MgrX','processes': [
#            {'name': 'ProcessA', 'outpipes':{ 1:'stdout',2:'stderr'} },
#            {'name': 'ProcessB', 'outpipes':{ 3:'stdout',4:'stderr'} },
#            ]
#       }
    send_msg(sock=sock, subport=0, message=json.dumps(msg) )


    while True:
        for (pname, proc, pipes) in process_list:

            pipes_inv = { v:k for (k,v) in pipes.items()}

            
            if proc.poll() is None:
                print("Polled")
                stdout_data = proc.stdout.readline()
                print("Polled XX")
                #stderr_data = proc.stderr.readline()
                stderr_data = "jkklJ".encode('utf-8')
                print("Read")

                if stdout_data:
                    send_msg(sock=sock, subport=pipes_inv['stdout'], message=stdout_data)
                if stderr_data:
                    send_msg(sock=sock, subport=pipes_inv['stderr'], message=stderr_data)


    sock.close()






def send_msg( sock, subport, message):
    print(type(message))
    if isinstance(message, bytes):
        msg_bytes = message
        pass # its all set.
    elif isinstance(message, str):
        msg_bytes = bytes(message, 'utf-8')
    else:
        assert(0)

    #msg_bytes = bytes(message, 'utf-8')
    sock.sendall( bytes("%d\n" % len(msg_bytes),'utf-8'  ) )
    sock.sendall( bytes('%d\n' % subport, 'utf-8') )
    sock.sendall( msg_bytes )



def client(message, ip, port):
    print ('Pretending to be client:Msg=%s' % message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        msg = {'name':'MgrX','processes':[
            {'name': 'ProcessA', 'outpipes':{ 1:'stdout',2:'stderr'} },
            {'name': 'ProcessB', 'outpipes':{ 3:'stdout',4:'stderr'} },
            ]
            }

        send_msg(sock=sock, subport=0, message=json.dumps(msg) )

        for i in range(100):
            time.sleep(1)
            print ("Sending: %s" % message)
            send_msg(sock=sock, subport=1, message="ProcA - StdOut1")
            send_msg(sock=sock, subport=2, message="ProcA - StdErr1")
            send_msg(sock=sock, subport=3, message="ProbB - StdOut2")
            send_msg(sock=sock, subport=4, message="ProcB - StdErr2")


    finally:
        sock.close()






if __name__ == "__main__":
    start_process_mgr('Mgr2')
    assert(0)



if __name__ == "__main__":

    HOST, PORT = "localhost", common.Ports.ProcessMgrs



    f = functools.partial( client, ip=HOST, port=PORT)
    trs = [Thread(target=f, args=["Mgr%d"%i]) for i in range(2)]
    for tr in trs:
        tr.daemon=True
        tr.start()


    for tr in trs:
        tr.join()


    time.sleep(2)




