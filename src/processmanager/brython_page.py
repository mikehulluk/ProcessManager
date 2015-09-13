from browser import alert, document as doc
from browser import websocket
from browser.html import BR

def on_open(evt):
    print("On-open called()")
    # Re-setup our button:
    btn = doc['btn_connect']
    btn.text = "Connected"
    btn.classList.remove('btn-warning')
    btn.classList.add('btn-success')
    btn.bind('click',close_socket)
    pass

def on_message(evt):
    div = doc['outputwindow']
    code= doc['outputcode']
    code <= BR() + evt.data
    div.scrollTop = div.scrollHeight;

def on_close(evt):
    print("OnClose() called")
    btn = doc['btn_connect']
    btn.text = "Connect.."
    btn.classList.remove('btn-success')
    btn.classList.add('btn-warning')
    doc['btn_connect'].bind('click', None) #_open)


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
    ws.bind('open',on_open)
    ws.bind('message',on_message)
    ws.bind('close',on_close)
    ws.bind('error',on_error)

def on_error(evt):
    global ws
    alert("Error")
    if ws is not None:
        print ("Closing socket (ERROR):")
        ws.close()

def close_socket(evt):
    global ws
    if ws is not None:
        print ("Closing socket:")
        ws.close()
        #ws=None
    #on_close(None)




#def send(ev):
#    data = doc["data"].value
#    if data:
#        ws.send(data)



doc['btn_connect'].bind('click', _open)
