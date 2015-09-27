#! /usr/bin/python3


import zmq
import sys

import random
import logging


import asyncio
import websockets as ws

import multiprocessing
from threading import Thread, Lock, local
import time

import json
import socket
import socketserver
import threading
import socketserver
import time

import pprint as pp
import common
from collections import defaultdict


# Basic logging info:
logging.basicConfig(level=logging.INFO)

# Be verbose with the logging:
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())



websockets_lock = Lock()
websockets = {}

connected_processes = {}



# Maps websockets to data to go out:
# {websocket -> ['hello','world']
websocket_data = defaultdict(list)

# Keep a list of connected processes:
#connected_processes = {
#    0: {'id':0, 'name':'Mgr1', 'processes': [
#        {'id':0, 'name':'Process1', 'start_time':None, 'outpipes':{1: 'stdout', 2:'stderr'}  },
#        {'id':1, 'name':'Process2', 'start_time':None, 'outpipes':{3: 'stdout', 4:'stderr'}  },
#                    ]
#            },
#
#    1: {'id':1, 'name':'Mgr2', 'processes': [
#        {'id':2, 'name':'Process1', 'start_time':None, 'outpipes':{1:'stdout',2:'stderr'}  },
#                    ]
#            },
#
#    2: {'id':2, 'name':'Mgr3', 'processes': [
#        {'id':4, 'name':'Process1', 'start_time':None, 'outpipes':{1:'stdout-stderr'}  },
#        {'id':5, 'name':'Process1', 'start_time':None, 'outpipes':{2:'stdout-stderr'}  },
#        {'id':6, 'name':'Process1', 'start_time':None, 'outpipes':{3:'stdout-stderr'}  },
#                    ]
#            },
#
#}












@asyncio.coroutine
def generate_content_cr():
    global websockets

    logger = logging.getLogger("Forwarding thread")
    logger.info("Started")

    while(1):
        time.sleep(1)

        # Clear out old sockets:
        with websockets_lock:
            websockets = {ws:mgr_id for (ws,mgr_id) in websockets.items() if ws.open}

        # Forward outstanding messages:
        with websockets_lock:
            for websocket in websockets:
                # Send all outstanding message
                for data in websocket_data[websocket]:
                    logger.info("Forwarding message to: %s --> %s" % (id(websocket), data))
                    yield from websocket.send(data)
                websocket_data[websocket] = []

def generate_content_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(generate_content_cr())
    asyncio.get_event_loop().run_forever()




print("Starting autogenerate thread")
tr_autogen = Thread(target=generate_content_thread)
# (Starting as a daemon means the thread will not prevent the process from exiting.)
tr_autogen.daemon = True
tr_autogen.start()









class WebSocketApi:
        OutputMsg = 'output'

        # Here -> websocket clients
        SendCfgProcMgrList = 'cfg-process-mgr-list'
        SendCfgProcMgrClosed = 'cfg-process-mgr-closed'
            
        # Here <- websocket clients
        RecvCfgSetProcMgr = "set-process-mgr"
        









class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):

    def read_msg(self):
            msg_size = self.rfile.readline()
            if not msg_size:
                return
            msg_size = int(msg_size)
            msg_subport = self.rfile.readline()
            if not msg_subport:
                return
            buff = b''
            while len(buff) < msg_size:
                to_read = msg_size - len(buff)
                x = self.rfile.read(to_read)
                if not x:
                    return
                buff += x

            subport = int(msg_subport.decode('utf-8').strip() )
            msg = buff.decode('utf-8')
            return (subport,msg)


    def handle(self):
        self.logger = logging.getLogger("TCP-Hander [%s]" % (id(self)) )
        self.logger.info("handle() called")

        self.procmgr_id = None

        while True:
            r = self.read_msg()
            if not r:
                self.logger.info("Connection closed")
                return
            (subport,msg) = r
            self.handleMsgMJHX( subport=subport, msg=msg )



    def handleMsgMJHX(self, subport, msg):
        self.logger.info('Handling Message -- subport:%d length:%d' %(subport, len(msg)) )
        self.logger.debug(msg)

        if subport == 0:
            # If its on subport 1, then it should be in json:
            self.logger.info('New process mgr added.')
            msg = json.loads(msg)
            self.logger.debug(msg)

            with websockets_lock:


                if connected_processes:
                    self.procmgr_id =  max( [ mgr['id'] for mgr in connected_processes.values() ]) + 1
                    next_proc_id = max( [ proc['id']  for mgr in connected_processes.values() for proc in mgr['processes'] ]) + 1
                else:
                    self.procmgr_id = 0
                    next_proc_id = 0

                msg['id'] = self.procmgr_id
                for (i,process) in enumerate(msg['processes']):
                    process['id'] = next_proc_id + i

                # Add to the list:
                connected_processes[self.procmgr_id] = msg
                pp.pprint(connected_processes)
                #print("Connected to %d" % len(connected_processes) )
                self.logger.info("Connected to %d" % len(connected_processes) )


        else:
            self.logger.info("Preparing to forward msg:")
            subport_str = str(subport)
            # Lookup the port:
            with websockets_lock:
                process, pipe_name = None,None
                for proc in connected_processes[self.procmgr_id]['processes']:
                    if subport_str in proc['outpipes']:
                        pipe_name = proc['outpipes'][subport_str]
                        process=proc
                        break

                assert(pipe_name and proc)


                # Ok, we can now send out a packet to each websocket:

                std_pkt = [ {'msg-type':WebSocketApi.OutputMsg ,'process_id':process['id'], 'pipe':pipe_name, 'contents':msg}]
                std_pkt_json = json.dumps(std_pkt)


                for (websocket, ws_procmgr_id) in websockets.items():
                    if self.procmgr_id != ws_procmgr_id:
                        continue
                    websocket_data[websocket].append(std_pkt_json)


    def finish(self):
        self.logger.info("Closing up socket")
        if not self.procmgr_id:
            return

        # Send a message to every connected websocket to say that teh 
        # this manager is now shut.
        for (websocket, ws_procmgr_id) in websockets.items():
            self.logger.info("Notifying websocket: %s" % id(websocket) )
            std_pkt = {'msg-type': WebSocketApi.SendCfgProcMgrClosed, 'process_mgr_id':self.procmgr_id }
            std_pkt_json = json.dumps([std_pkt])
            websocket_data[websocket].append(std_pkt_json)



        with websockets_lock:
            del connected_processes[self.procmgr_id]




class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass



def build_tcpserver():
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", common.Ports.ProcessMgrs

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()



print ("Launching tcp server:")
tr_tcp = Thread(target=build_tcpserver)
# (Starting as a daemon means the thread will not prevent the process from exiting.)
#tr_tcp.daemon = True
tr_tcp.start()




















@asyncio.coroutine
def websocket_handler(websocket, path):
    logger = logging.getLogger("Websocket-Hander [%s]" % (id(websocket)) )
    logger.info("websocket_handle() called")

    # Send the initial message:
    init_data = [
            {
            'msg-type': WebSocketApi.SendCfgProcMgrList,
            'process_mgrs': list( connected_processes.values() )
            }
            ]

    #pp.pprint(connected_processes)


    init_data_s = json.dumps(init_data) # , separators=(',',':'))
    yield from websocket.send(init_data_s)

    # Add the websocket to the list:
    with websockets_lock:
        websockets[websocket] = None


    while 1:
        msg_ins  = yield from websocket.recv()
        #print ("Data in!! %s", msg_ins)

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

            if msg_type==WebSocketApi.RecvCfgSetProcMgr: #"set-process-mgr":

                mgr_id = int( msg['process-mgr-id'] )
                process_mgr_data = connected_processes[mgr_id]

                return_msg = {'msg-type': 'cfg-process-mgr-details'}
                return_msg.update(process_mgr_data)


                init_data_s = json.dumps([return_msg], separators=(',',':'))
                yield from websocket.send(init_data_s)

                # And store which process_mgr the websocket is interested in:
                with websockets_lock:
                    websockets[websocket] = mgr_id

            else:
                print ("Unhandled msg-type: %s" % msg_type)









def websockets_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = ws.serve(websocket_handler, 'localhost', common.Ports.Websocket)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()



# And launch the websockets server in a new thread::
print ("Launching websockets server:")
tr_websockets = Thread(target=websockets_thread)
# (Starting as a daemon means the thread will not prevent the process from exiting.)
#tr_websockets.daemon = True
tr_websockets.start()





















try:
    #tr.join()
    tr_websockets.join()
    tr_tcp.join()
except:
    print( "Exception Raise")
    print( "TODO:: KILL THREADS")
    raise
