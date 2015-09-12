from browser import alert, document as doc
from browser import websocket

def on_open(evt):
    doc['sendbtn'].disabled = False
    doc['closebtn'].disabled = False
    doc['openbtn'].disabled = True

def on_message(evt):
    # message reeived from server
    alert("Message received : %s" %evt.data)

def on_close(evt):
    # websocket is closed
    alert("Connection is closed")
    doc['openbtn'].disabled = False
    doc['closebtn'].disabled = True
    doc['sendbtn'].disabled = True

ws = None
def _open(ev):
    print ("Hello")
    if not __BRYTHON__.has_websocket:
        alert("WebSocket is not supported by your browser")
        return
    global ws
    # open a web socket
    #ws = websocket.WebSocket("wss://echo.websocket.org")
    ws = websocket.WebSocket("ws://localhost:8765")
    # bind functions to web socket events
    ws.bind('open',on_open)
    ws.bind('message',on_message)
    ws.bind('close',on_close)

def send(ev):
    data = doc["data"].value
    if data:
        ws.send(data)

def close_connection(ev):
    ws.close()
    doc['openbtn'].disabled = False

doc['openbtn'].bind('click', _open)
doc['sendbtn'].bind('click', send)
doc['closebtn'].bind('click', close_connection)
