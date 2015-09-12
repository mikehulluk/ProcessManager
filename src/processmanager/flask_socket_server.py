#!/usr/bin/env python3

from flask import Flask

from flask import Flask, request, send_from_directory
app = Flask(__name__, static_url_path='')


header = """
<html>
<head>
<script src="/js/brython/brython.js"></script>
</head>
<body onload="brython({debug:1})">
<script type="text/python">
"""
footer = """
</script>

<button id="openbtn">Open connection</button>
<br><input id="data"><button id="sendbtn" disabled>Send</button>
<p><button id="closebtn" disabled>Close connection</button>

</body>
</html>
"""


@app.route('/js/brython/<path:path>')
def send_js(path):
    src_dir = "/home/michael/dev/ProcessManager/src/processmanager/brython/www/src"
    return send_from_directory(src_dir, path)


@app.route('/')
def br():
    with open('brython_page.py') as f:
        return header + f.read() + footer
    #return header


if __name__ == '__main__':
    app.run(debug=True)
