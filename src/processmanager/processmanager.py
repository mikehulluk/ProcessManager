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
    websockets_lock.acquire()
    websockets.append(websocket)
    websockets_lock.release()

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
    websockets_lock.acquire()
    websockets.remove(websocket)
    websockets_lock.release()






@asyncio.coroutine
def generate_content(): 
    print ("Starting generate content:")
    while(1):
        time.sleep(1)

        websockets_lock.acquire()
        print ("Sending content..")
        print ("NWebsockets: %d" % len(websockets))
        for websocket in websockets:

            if websocket.open:
                yield from websocket.send("GENERATED_CONTENT")
        websockets_lock.release()


def generate_content_(): 
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(generate_content())
    asyncio.get_event_loop().run_forever()



print ("Started thread")
tr = Thread(target=generate_content_, )
tr.start()
print ("Thread started")



print ("Launching server:")
start_server = ws.serve(hello, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()




