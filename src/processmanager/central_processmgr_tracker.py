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

from types import MethodType


@asyncio.coroutine
def _ws_send_msg(self, msg ):
    yield from self.send(json.dumps([msg]))


ws.WebSocketServerProtocol.send_msg = _ws_send_msg
# # Monkey patch websockets to add:
# #  * send_msg()
# #  * send_msgs()
# # functions.
# 
# 
# #yield from websocket.send(json.dumps([init_data]))
# print( websocket.WebSocketServerProtocol )










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



websocket_data = defaultdict(list)

threadedtcprequesthandler_to_procmgr_id = {} #(socketserver.StreamRequestHandler):



class ConnectionMgr(object):
    @classmethod
    def process_mgr_open_connection(cls, socket, connection_msg):
        print(connection_msg)
        msg = connection_msg

        with websockets_lock:
            if connected_processes:
                procmgr_id =  max( [ mgr['id'] for mgr in connected_processes.values() ]) + 1
                next_proc_id = max( [ proc['id']  for mgr in connected_processes.values() for proc in mgr['processes'] ]) + 1
            else:
                procmgr_id = 0
                next_proc_id = 0

            msg['id'] = procmgr_id
            for (i,process) in enumerate(msg['processes']):
                process['id'] = next_proc_id + i

            # Add to the list:
            connected_processes[procmgr_id] = msg
            pp.pprint(connected_processes)
            #print("Connected to %d" % len(connected_processes) )
            threadedtcprequesthandler_to_procmgr_id[socket] = procmgr_id
            socket.logger.info("Connected to %d" % len(connected_processes) )

    @classmethod
    def process_mgr_close_connection(cls, socket):

        procmgr_id = threadedtcprequesthandler_to_procmgr_id[socket]
        if procmgr_id is None:
            return

        # Send a message to every connected websocket to say that teh
        # this manager is now shut.
        socket.logger.info("Closing up socket")
        for (websocket, ws_procmgr_id) in websockets.items():
            socket.logger.info("Notifying websocket: %s" % id(websocket) )
            std_pkt = {'msg-type': WebSocketApi.SendCfgProcMgrClosed, 'process_mgr_id':procmgr_id }
            std_pkt_json = json.dumps([std_pkt])
            websocket_data[websocket].append(std_pkt_json)



        with websockets_lock:
            del connected_processes[procmgr_id]

    @classmethod
    def process_mgr_recv_output_data(cls, socket, subport, msg):
        subport_str = str(subport)
        # Lookup the port:
        with websockets_lock:
            process, pipe_name = None,None

            procmgr_id = threadedtcprequesthandler_to_procmgr_id[socket]


            for proc in connected_processes[procmgr_id]['processes']:
                if subport_str in proc['outpipes']:
                    pipe_name = proc['outpipes'][subport_str]
                    process=proc
                    break

            assert(pipe_name and proc)


            # Ok, we can now send out a packet to each websocket:

            std_pkt = [ {'msg-type':WebSocketApi.OutputMsg ,'process_id':process['id'], 'pipe':pipe_name, 'contents':msg}]
            std_pkt_json = json.dumps(std_pkt)

            procmgr_id = threadedtcprequesthandler_to_procmgr_id[socket]

            for (websocket, ws_procmgr_id) in websockets.items():
                if procmgr_id != ws_procmgr_id:
                    continue
                websocket_data[websocket].append(std_pkt_json)


    @classmethod
    def websocket_open_connection(cls, websocket):

        # Add the websocket to the list:
        with websockets_lock:
            websockets[websocket] = None

    @classmethod
    def websocket_cfg_set_process_mgr(cls, websocket, mgr_id):
        with websockets_lock:
            websockets[websocket] = mgr_id

    @classmethod
    def websocket_close_connection(cls, websocket):
        with websockets_lock:
            del websockets[websocket]


    @classmethod
    def websocket_ensure_all_sockets_open(cls,):
        global websockets
        with websockets_lock:
            for (ws,mgr_id) in websockets.items():
                assert (ws.open)
        websockets = {ws:mgr_id for (ws,mgr_id) in websockets.items() if ws.open}

    @classmethod
    def websocket_get_outstanding_data_messages(cls, websocket, clear=True):
        res =  websocket_data[websocket]
        if clear:
            websocket_data[websocket] = []
        return res


    @classmethod
    def websocket_get_active_sockets(cls,):
        return websockets.keys()






class MsgBuilderWebsocket(object):
    @classmethod
    def createSendCfgProcMgrList(cls):
        init_data = {
            'msg-type': WebSocketApi.SendCfgProcMgrList,
            'process_mgrs': list( connected_processes.values() )
            }
        return init_data

    @classmethod
    def createSendCfgProcMgrDetails(cls, mgr_id):
        process_mgr_data = connected_processes[mgr_id]
        return_msg = {'msg-type': WebSocketApi.SendCfgProcMgrDetails}
        return_msg.update(process_mgr_data)
        return return_msg













# ------------ Our forwarding thread ----------------
# ---------------------------------------------------

@asyncio.coroutine
def forward_to_websocket_cr():
    global websockets

    logger = logging.getLogger("Forwarding thread")
    logger.info("Started")

    while(1):
        time.sleep(0)
        # Clear out old sockets:
        ConnectionMgr.websocket_ensure_all_sockets_open()

        # Forward outstanding messages:
        with websockets_lock:
            for websocket in ConnectionMgr.websocket_get_active_sockets():
                for data in ConnectionMgr.websocket_get_outstanding_data_messages(websocket, clear=True): 
                    logger.info("Forwarding message to: %s --> %s" % (id(websocket), data))
                    yield from websocket.send(data)

def forward_to_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(forward_to_websocket_cr())
    asyncio.get_event_loop().run_forever()

def start_thread_websocket_forwarding():
    print("Starting autogenerate thread")
    tr_autogen = Thread(target=forward_to_websocket_thread)
    # (Starting as a daemon means the thread will not prevent the process from exiting.)
    tr_autogen.daemon = True
    tr_autogen.start()
    return tr_autogen









class WebSocketApi: OutputMsg = 'output'

        # Here -> websocket clients
        SendCfgProcMgrList = 'cfg-process-mgr-list'
        SendCfgProcMgrClosed = 'cfg-process-mgr-closed'
        SendCfgProcMgrDetails = 'cfg-process-mgr-details'

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

        threadedtcprequesthandler_to_procmgr_id[self] = None

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
            # If its on subport 0, then its a control message and it should be in json:

            self.logger.info('New process-mgr found')
            msg = json.loads(msg)
            self.logger.debug(msg)

            ConnectionMgr.process_mgr_open_connection(socket=self, connection_msg=msg)

        else:
            self.logger.info("Preparing to forward msg:")
            ConnectionMgr.process_mgr_recv_output_data(socket=self, subport=subport, msg=msg)


    def finish(self):
        self.logger.info("Closing up socket")
        ConnectionMgr.process_mgr_close_connection(socket=self)




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


def start_thread_process_mgr_listener():
    print ("Launching tcp server:")
    tr_tcp = Thread(target=build_tcpserver)
    # (Starting as a daemon means the thread will not prevent the process from exiting.)
    #tr_tcp.daemon = True
    tr_tcp.start()
    return tr_tcp




















@asyncio.coroutine
def websocket_handler(websocket, path):
    logger = logging.getLogger("Websocket-Hander [%s]" % (id(websocket)) )
    logger.info("websocket_handle() called")

    ConnectionMgr.websocket_open_connection(websocket=websocket)


    # Send the initial message:
    init_data = MsgBuilderWebsocket.createSendCfgProcMgrList() 
    yield from websocket.send_msg(init_data)



    # Msg loop:
    while 1:
        msg_ins  = yield from websocket.recv()

        # Has the socket closed?
        if msg_ins is None:
            ConnectionMgr.websocket_close_connection(cls, websocket)
            logger.log("Socket closed. (By remote?)")
            return


        # Otherwise, lets handle the data:
        msgs = json.loads(msg_ins)

        for msg in msgs:
            msg_type = msg['msg-type']

            if msg_type==WebSocketApi.RecvCfgSetProcMgr:

                mgr_id = int( msg['process-mgr-id'] )

                # Store which process_mgr the websocket is interested in:
                ConnectionMgr.websocket_cfg_set_process_mgr(websocket=websocket, mgr_id=mgr_id)

                # And send back the configuration info:
                msg = MsgBuilderWebsocket.createSendCfgProcMgrDetails(mgr_id=mgr_id)
                yield from websocket.send_msg(msg)


            else:
                print ("Unhandled msg-type: %s" % msg_type)









def websockets_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = ws.serve(websocket_handler, 'localhost', common.Ports.Websocket)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()



def start_thread_websocket_listener():
    # And launch the websockets server in a new thread::
    print ("Launching websockets server:")
    tr_websockets = Thread(target=websockets_thread)
    # (Starting as a daemon means the thread will not prevent the process from exiting.)
    #tr_websockets.daemon = True
    tr_websockets.start()
    return tr_websockets
    




















try:
    tr_ws_forwarding = start_thread_websocket_forwarding()
    tr_tcp = start_thread_process_mgr_listener()
    tr_websockets = start_thread_websocket_listener():
    #tr.join()
    tr_websockets.join()
    tr_tcp.join()
except:
    print( "Exception Raise")
    print( "TODO:: KILL THREADS")
    raise

