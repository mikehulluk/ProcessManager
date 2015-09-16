#! /usr/bin/python3


import zmq
import sys

import random
import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())


import asyncio
import websockets as ws

import multiprocessing
from threading import Thread, Lock
import time

import json

websockets = []
websockets_lock = Lock()



@asyncio.coroutine
def websocket_handler(websocket, path):

    init_data = [
            {
            'msg-type':'config',
            'config':{
                'process_mgrs': [
                        {'id':0, 'name':'Mgr1', 'processes': [
                            {'id':0, 'name':'Process1', 'start_time':None, 'outpipes':['stdout','stderr']  },
                            {'id':1, 'name':'Process2', 'start_time':None, 'outpipes':['stdout','stderr']  },
                            ]
                        },
                        #{'id':1, 'name':'Mgr2', 'processes': [
                        #    {'id':2, 'name':'Process1', 'start_time':None, 'outpipes':['stdout','stderr']  },
                        #    {'id':3, 'name':'Process2', 'start_time':None, 'outpipes':['stdout','stderr']  },
                        #    ]
                        #},
                        ]
            }
        }
            ]

    init_data = [
            {
            'msg-type':'cfg-process-mgr-list',
            'process_mgrs': [
                {'id':0, 'name':'Mgr1'},
                {'id':1, 'name':'Mgr2'},
                {'id':2, 'name':'Mgr2'},
            ]
            }
            ]


    init_data_s = json.dumps(init_data, separators=(',',':'))
    yield from websocket.send(init_data_s)

    # Add the websocket to the list:
    with websockets_lock:
        websockets.append(websocket)

    #time.sleep(10)

    #print ("Connection openned")
    #name = yield from websocket.recv()
    #print("< {}".format(name))
    #greeting = "Hello {}!".format(name)
    #yield from websocket.send(greeting)
    #print("> {}".format(greeting))
    
    name = yield from websocket.recv()
    print ("Data in!! %s", name)

    time.sleep(5)

    init_data = [
            {
            'msg-type':'cfg-process-mgr-details',
            'id':0, 
            'name':'Mgr1', 
            'processes': [
                            {'id':0, 'name':'Process1', 'start_time':None, 'outpipes':['stdout','stderr']  },
                            {'id':1, 'name':'Process2', 'start_time':None, 'outpipes':['stdout','stderr']  },
                            ]
                        },
            ]
    init_data_s = json.dumps(init_data, separators=(',',':'))
    print("Sending cfg-process-mgr-details")
    yield from websocket.send(init_data_s)


    name = yield from websocket.recv()
    time.sleep(5)
    while True:
        name = yield from websocket.recv()
        if name:
            print(name)



    #name = yield from websocket.recv()
    #print("< {}".format(name))
    #greeting = "Hello - round2 {}!".format(name)
    #yield from websocket.send(greeting)
    #print("> {} (round2)".format(greeting))

    # Remove the websocket:
    with websockets_lock:
        websockets.remove(websocket)





@asyncio.coroutine
def generate_content_cr():
    print ("Starting generate content:")

    port = "5556"
    if len(sys.argv) > 1:
        port =  sys.argv[1]
        int(port)

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % port)


    while(1):
        #time.sleep(1)

        #send_data = "GENERATED_CONTENT"
        #send_data = "GENERATED_CONTENT"
        time.sleep(10)

        stdout_data = socket.recv()
        send_data = str(stdout_data) 

        pipe = random.choice(['stderr','stdout'])
        proc_id = random.randint(0,1) 

        std_pkt = [ {'msg-type':'output','process_id':proc_id, 'pipe':pipe, 'contents':send_data}]
        std_pkt_json = json.dumps(std_pkt)


        with websockets_lock:
            print ("Sending content..")
            print ("NWebsockets: %d" % len(websockets))
            for websocket in websockets:

                if websocket.open:
                    #yield from websocket.send(send_data)
                    yield from websocket.send(std_pkt_json)


def generate_content_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(generate_content_cr())
    asyncio.get_event_loop().run_forever()




# Spawn off the thread to take of reading input and forwarding it up to the web-sockets:
print ("Started thread")
tr = Thread(target=generate_content_thread, )
tr.start()



# And launch the websockets server:
print ("Launching server:")
start_server = ws.serve(websocket_handler, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()




