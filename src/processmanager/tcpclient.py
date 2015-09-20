
# New structure - handle incoming socket requests manually:
import socket
import threading
import socketserver
import time

import json


def send_msg( sock, subport, message):
    msg_bytes = bytes(message, 'utf-8')
    sock.sendall( bytes("%d\n" % len(msg_bytes),'utf-8'  ) )
    sock.sendall( bytes('%d\n' % subport, 'utf-8') )
    sock.sendall( msg_bytes )



def client(ip, port, subport, message):
    print ('Pretending to be client:Msg=%s' % message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        msg = {'name':'MgrX','outports':{1:'stdout',2:'stderr'}}
        send_msg(sock=sock, subport=0, message=json.dumps(msg) )
        send_msg(sock=sock, subport=1, message="StdOut1")
        send_msg(sock=sock, subport=2, message="StdErr1")
        send_msg(sock=sock, subport=1, message="StdOut2")
        send_msg(sock=sock, subport=2, message="StdErr2")
        #send_msg(sock=sock, subport=subport, message=message)
        #msg_bytes = bytes(message, 'utf-8')
        #sock.sendall( bytes("%d\n" % len(msg_bytes),'utf-8'  ) )
        #sock.sendall( bytes('%d\n' % subport, 'utf-8') )
        #sock.sendall( msg_bytes )
    finally:
        sock.close()










if __name__ == "__main__":
    client('127.0.0.1', 6000, 0, "Hello World 1")
    client('127.0.0.1', 6000, 1, "Hello World 1")
    client('127.0.0.1', 6000, 2, "Hello World 1")

    time.sleep(2)
    #client(ip, port, "Hello World 2")
    #client(ip, port, "Hello World 3")
    #build_tcpserver()
