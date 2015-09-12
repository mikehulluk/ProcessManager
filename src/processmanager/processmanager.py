#! /usr/bin/python3



#processes = [
#    # id, caption, command, 
#    (None, "Proc1", """cat "hello" """,)
#    (None, "Proc2", """cat "hello" """,)
#
#        ]
import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())


import asyncio
import websockets as ws

import multiprocessing
#from multiprocessing import Process, Queue
from threading import Thread, Lock
import time
websockets = []
websockets_lock = Lock()



@asyncio.coroutine
def hello(websocket, path):

    # Add the websocket to the list:
    with websockets_lock:
        websockets.append(websocket)

    print ("Connection openned")
    name = yield from websocket.recv()
    print("< {}".format(name))
    greeting = "Hello {}!".format(name)
    yield from websocket.send(greeting)
    print("> {}".format(greeting))

    websocket.send("JLKJ")

    name = yield from websocket.recv()
    print("< {}".format(name))
    greeting = "Hello - round2 {}!".format(name)
    yield from websocket.send(greeting)
    print("> {} (round2)".format(greeting))

    # Remove the websocket:
    with websockets_lock:
        websockets.remove(websocket)






@asyncio.coroutine
def generate_content_cr(): 
    print ("Starting generate content:")
    while(1):
        time.sleep(1)
        send_data = "GENERATED_CONTENT"

        with websockets_lock:
            print ("Sending content..")
            print ("NWebsockets: %d" % len(websockets))
            for websocket in websockets:

                if websocket.open:
                    yield from websocket.send(send_data)


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
start_server = ws.serve(hello, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()




