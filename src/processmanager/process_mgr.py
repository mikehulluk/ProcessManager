import zmq
import random
import sys
import time

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

while True:
    time.sleep(1)
    #msg = socket.recv()
    #print msg
    print("Sending mgs")
    socket.send("client message to server1")
    socket.send("client message to server2")
    time.sleep(1)
