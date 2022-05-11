from flask import Flask
import zmq
import click

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho


class WebServer(object):

    def __init__(self, port, context):
        self.local_interface_dealer = context.socket(zmq.DEALER)
        self.local_interface_dealer.connect(f"inproc://local_interface")

    def handle_requests(self):
        pass

def run_webserver(args, context):
    host_name = "0.0.0.0"
    port = args.web_interface_port
    web_server = WebServer(args.web_interface_port, context)
    app = Flask(__name__)
    app.route('/', web_server.handle_requests)
    app.run(host=host_name, port=args.web_server_port, debug=False, use_reloader=False)

