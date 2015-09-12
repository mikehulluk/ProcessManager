#! /usr/bin/python3



#processes = [
#    # id, caption, command, 
#    (None, "Proc1", """cat "hello" """,)
#    (None, "Proc2", """cat "hello" """,)
#
#        ]


import asyncio
import websockets

@asyncio.coroutine
def hello(websocket, path):
    name = yield from websocket.recv()
    print("< {}".format(name))
    greeting = "Hello {}!".format(name)
    yield from websocket.send(greeting)
    print("> {}".format(greeting))

print ("Launching server:")
start_server = websockets.serve(hello, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
