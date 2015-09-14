import zmq
import random
import sys
import time
import datetime

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

while True:
    time.sleep(0.05)
    #msg = socket.recv()
    print("Sending mgs")
    t = datetime.datetime.now().strftime("%H:%M:%S  on %B %d, %Y")
    r = "%02x" % random.randint(0,255)
    socket.send("client message to server " + t + " ->> " + r)
