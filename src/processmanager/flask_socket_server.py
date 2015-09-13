#!/usr/bin/env python3

from flask import Flask

from flask import Flask, request, send_from_directory
app = Flask(__name__, static_url_path='')


header = """
<html>
<head>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>

<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">

<!-- Optional theme -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css">

<!-- Latest compiled and minified JavaScript -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>


<script src="/js/brython/brython.js"></script>
</head>
<body onload="brython({debug:1})">
<script type="text/python">
"""
footer = """
</script>



    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">Project name</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="#">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </nav>

    <div class="container">

      <div class="starter-template">
        <h1>Bootstrap starter template</h1>
        <p class="lead">Use this document as a way to quickly start any new project.<br> All you get is this text and a mostly barebones HTML document.</p>


        <button id="openbtn">Open connection</button>
        <input id="data"><button id="sendbtn" disabled>Send</button>
        <button id="closebtn" disabled>Close connection</button>
        
        <div  id='outputwindow' style="overflow:scroll; height:250px;">
        <code  id='outputcode' />
        </div>

      </div>

    </div><!-- /.container -->

</body>
</html>
"""


@app.route('/js/<path:path>')
def send_js(path):
    src_dir = "/home/michael/dev/ProcessManager/www/js/"
    return send_from_directory(src_dir, path)

@app.route('/css/<path:path>')
def send_css(path):
    src_dir = "/home/michael/dev/ProcessManager/www/css/"
    return send_from_directory(src_dir, path)

@app.route('/')
def br():
    with open('brython_page.py') as f:
        return header + f.read() + footer
    #return header


if __name__ == '__main__':
    app.run(debug=True)
