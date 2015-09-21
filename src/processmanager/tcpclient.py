
# New structure - handle incoming socket requests manually:
import socket
import threading
import socketserver
import time

import json
import functools
from threading import Thread


def send_msg( sock, subport, message):
    msg_bytes = bytes(message, 'utf-8')
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

        for i in range(10):
            time.sleep(50)
            print ("Sending: %s" % message)
            send_msg(sock=sock, subport=1, message="ProcA - StdOut1")
            send_msg(sock=sock, subport=2, message="ProcA - StdErr1")
            send_msg(sock=sock, subport=3, message="ProbB - StdOut2")
            send_msg(sock=sock, subport=4, message="ProcB - StdErr2")


    finally:
        sock.close()









if __name__ == "__main__":
    #client('127.0.0.1', 6000, 0, "Hello World 1")
    #client('127.0.0.1', 6000, 1, "Hello World 1")
    #client('127.0.0.1', 6000, 2, "Hello World 1")

    HOST, PORT = "localhost", 6003



    f = functools.partial( client, ip=HOST, port=PORT)
    trs = [Thread(target=f, args=["Mgr%d"%i]) for i in range(5)]
    for tr in trs:
        tr.daemon=True
        tr.start()


    for tr in trs:
        tr.join()


    time.sleep(2)




