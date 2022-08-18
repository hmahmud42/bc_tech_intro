"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Web-server for the local interface.
"""
from flask import Flask
import zmq
import click

import logging
from blockchain_proto.consts import GET_UNADDED_TRANS, GET_BLOCKCHAIN, ADD_TRANS


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


def run_webserver(web_interface_port, context):
    host_name = "0.0.0.0"
    web_server = WebServer(web_interface_port, context)
    app = Flask(__name__)
    app.route('/', web_server.handle_requests)
    app.route(f'/{}')
    app.run(host=host_name, port=web_interface_port, debug=False, use_reloader=False)

