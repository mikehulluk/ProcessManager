#!/usr/bin/env python3

import string
from flask import Flask

from flask import Flask, request, send_from_directory
app = Flask(__name__, static_url_path='')


pkg_root = "/home/mike/dev/ProcessManager/"
@app.route('/js/<path:path>')
def send_js(path):
    src_dir = pkg_root + "/www/js/"
    return send_from_directory(src_dir, path)

@app.route('/css/<path:path>')
def send_css(path):
    src_dir = pkg_root + "/www/css/"
    return send_from_directory(src_dir, path)

@app.route('/')
def br():
    with open('page.html.tmpl') as ftmpl:
        with open('brython_page.py') as f:
            tmpl = string.Template( ftmpl.read() )
            return tmpl.substitute(brython_script=f.read())


if __name__ == '__main__':
    app.run(debug=True)
