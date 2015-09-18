#! /usr/bin/python3


import zmq
import sys

import random
import logging


import asyncio
import websockets as ws

import multiprocessing
from threading import Thread, Lock
import time

import json



# Be verbose with the logging:
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())




websockets = {}
websockets_lock = Lock()





# Keep a list of connected processes:
connected_processes = {
    0: {'id':0, 'name':'Mgr1', 'processes': [
              {'id':0, 'name':'Process1', 'start_time':None, 'outpipes':['stdout','stderr']  },
              {'id':1, 'name':'Process2', 'start_time':None, 'outpipes':['stdout','stderr']  },
                    ]
            },

    1: {'id':1, 'name':'Mgr2', 'processes': [
              {'id':2, 'name':'Process1', 'start_time':None, 'outpipes':['stdout','stderr']  },
                    ]
            },

    2: {'id':2, 'name':'Mgr3', 'processes': [
              {'id':4, 'name':'Process1', 'start_time':None, 'outpipes':['stdout-stderr']  },
              {'id':5, 'name':'Process1', 'start_time':None, 'outpipes':['stdout-stderr']  },
              {'id':6, 'name':'Process1', 'start_time':None, 'outpipes':['stdout-stderr']  },
                    ]
            },

}




@asyncio.coroutine
def websocket_handler(websocket, path):

    print("Connection openned")


    init_data = [
            {
            'msg-type':'cfg-process-mgr-list',
            'process_mgrs': list( connected_processes.values() )
            }
            ]


    init_data_s = json.dumps(init_data, separators=(',',':'))
    yield from websocket.send(init_data_s)

    # Add the websocket to the list:
    with websockets_lock:
        websockets[websocket] = None #.append(websocket)


    while 1:


        msg_ins  = yield from websocket.recv()
        print ("Data in!! %s", msg_ins)

        # Has the socket closed?
        if msg_ins is None:
            print("Socket closed. (By remote?)")
            with websockets_lock:
                del websockets[websocket]
            return


        # Otherwise, lets handle the data:
        msgs = json.loads(msg_ins)

        for msg in msgs:
            msg_type = msg['msg-type']

            if msg_type=="set-process-mgr":

                mgr_id = int( msg['process-mgr-id'] )
                process_mgr_data = connected_processes[mgr_id]

                return_msg = {'msg-type': 'cfg-process-mgr-details'}
                return_msg.update(process_mgr_data)


                init_data_s = json.dumps([return_msg], separators=(',',':'))
                print("Sending cfg-process-mgr-details")
                print(return_msg)
                yield from websocket.send(init_data_s)

                # And store which process_mgr the websocket is interested in:
                with websockets_lock:
                    websockets[websocket] = mgr_id

            else:
                print ("Unhandled msg-type: %s" % msg_type)








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
        #time.sleep(1)

        stdout_data = socket.recv()
        send_data = str(stdout_data)

        procmgr_id = random.choice( list(connected_processes.keys() ) )
        process = random.choice( list( connected_processes[procmgr_id]['processes'] ) )
        pipe = random.choice( list( process['outpipes'] ) )


        #pipe = random.choice(['stderr','stdout'])
        #proc_id = random.randint(0,1)

        std_pkt = [ {'msg-type':'output','process_id':process['id'], 'pipe':pipe, 'contents':send_data}]
        std_pkt_json = json.dumps(std_pkt)


        with websockets_lock:
            print ("Sending content..")
            print ("NWebsockets: %d" % len(websockets))
            for (websocket, ws_procmgr_id) in websockets.items():
                if procmgr_id != ws_procmgr_id:
                    continue

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




def websockets_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = ws.serve(websocket_handler, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()



# And launch the websockets server in a new thread::
print ("Launching server:")
tr_websockets = Thread(target=websockets_thread)
tr_websockets.start()


try:
    tr.join()
    tr_websockets.join()
except:
    print( "Exception Raise")
    print( "TODO:: KILL THREADS")
    raise
