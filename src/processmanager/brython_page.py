from browser import alert, document as doc
from browser import websocket
from browser.html import BR, DIV, H2, H3,H4, CODE
import json



def on_open(evt):
    # Re-setup our button:
    btn = doc['btn_connect']
    btn.text = "Connected"
    btn.classList.remove('btn-warning')
    btn.classList.add('btn-success')

    btn.bind('click', btnClkDisonnect)



def on_close(evt):
    btn = doc['btn_connect']
    btn.text = "Connect.."
    btn.classList.remove('btn-success')
    btn.classList.add('btn-warning')

    btn.bind('click', btnClkConnect)


def on_message(evt):
    div = doc['outputwindow']
    code= doc['outputcode']
    code <= BR() + evt.data
    div.scrollTop = div.scrollHeight;

    handle_msg(evt.data)

def btnClkConnect(evt):
    evt.stopPropagation()
    _open(evt)

def btnClkDisonnect(evt):
    evt.stopPropagation()
    ws.close()

ws = None
def _open(ev):
    if not __BRYTHON__.has_websocket:
        alert("WebSocket is not supported by your browser")
        return
    global ws

    # open a web socket
    ws = websocket.WebSocket("ws://localhost:8765")

    ws.bind('open',on_open)
    ws.bind('message',on_message)
    ws.bind('close',on_close)
    ws.bind('error',on_error)

def on_error(evt):
    global ws
    if ws is not None:
        ws.close()

def close_socket(evt):
    evt.stopPropagation()
    global ws
    if ws is not None:
        ws.close()







def handle_msg(data):
    print("Handling msg:")
    msgs = json.loads(data)
    print(msgs)
    for msg in msgs:
        msg_type=msg['msg-type']
        print(msg_type)
        if msg_type=='config':
            handle_msg_config(msg)
        if msg_type=='output':
            handle_msg_output(msg)

# Map (process_id, pipe_name) => code-html node
code_blks = {}
def handle_msg_config(msg):
    global code_blks

    config = msg['config']

    # Clear out the old contents from process_container:
    ctn = doc['ctn_process']
    code_blks = {}
    ctn.clear()



    for process_mgr in config['process_mgrs']:
        print("Process Mgr")
        print(process_mgr)
        process_mgr_name = process_mgr['name']

        for process in process_mgr['processes']:
            process_name = process['name']
            process_id = process['id']

            heading = DIV("[%s] %s (%d)"%(process_mgr_name, process_name, process_id), Class="panel-heading")
            contents = ""#H2(process_name)
            new_div = DIV(heading + DIV(contents, Class="panel-body"), Class="panel panel-default" )   
            ctn <= new_div

            for output_pipe in process['outpipes']:
                print ("output_pipe",output_pipe)
                nCode = CODE("XX",id="jlk")
                container = DIV( DIV( nCode,style={'overflow':'scroll','height':'150px'}),
                            Class='container')
                new_div <= H3(output_pipe, )
                new_div <= container
                code_blks[ (process_id, output_pipe) ] = nCode


def handle_msg_output(msg):
    global code_blks

    proc_id = msg['process_id']
    pipe_name = msg['pipe']

    codeBlock = code_blks[ (proc_id,pipe_name) ]
    codeBlock <= BR() + msg['contents']
    codeBlock.parentNode.scrollTop = codeBlock.parentNode.scrollHeight;


doc['btn_connect'].bind('click', btnClkConnect)
