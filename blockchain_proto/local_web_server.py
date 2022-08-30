"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Web-server for the local interface.
"""
import logging
import pickle

from flask import Flask, request
from flask_cors import CORS, cross_origin
import click
import zmq
from blockchain_proto.consts import GET_UNADDED_TRANS, GET_BLOCKCHAIN, ADD_TRANS, \
    GET_BLOCKCHAIN_ROUTE, GET_UNADDED_TRANS_ROUTE, ADD_TRANS_ROUTE
from blockchain_proto.transactions.transaction import Transaction
from blockchain_proto.messages import log_info


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho


class LIWebServer:
    """
    Webserver that serves the local interface to the node.

    Parameters
    ----------

    args: argparse.Namespace
        The arguments received from the command line.

    context: zmq.Context
        The context to use to create the socket to connect to the
        zmq interface.
    """
    def __init__(self, args, context):
        self.context = context
        self.server_port = str(int(args.base_port) + 2)
        self.client_sock = self.context.socket(zmq.DEALER)
        self.client_sock.connect("inproc://local_interface")

    @cross_origin()
    def get_blockchain(self):
        """
        Endpoint function that returns the blockchain represented as a string
        back to the requesting source. 
        """
        self.client_sock.send_multipart([GET_BLOCKCHAIN])    
        data = self.client_sock.recv_multipart()
        ret_val = pickle.loads(data[1])
        return ret_val

    @cross_origin()
    def get_unadded_trans(self):
        """
        Endpoint function that returns the unadded transactions  represented as a string
        back to the requesting source. 
        """
        self.client_sock.send_multipart([GET_UNADDED_TRANS])    
        data = self.client_sock.recv_multipart()
        ret_val = pickle.loads(data[1])
        return ret_val

    @cross_origin()
    def add_trans(self):
        """
        Endpoint function that adds the transactions represented as dictionaries
        to the blockchain.
        """
        trans_list_json = request.json
        trans_list = [Transaction.from_dict(trans_json) for trans_json in trans_list_json]
        invalid_list = [f"Error: {trans}" for trans in trans_list if isinstance(trans, str)]
        if len(invalid_list) > 0:
            return "Transactions not added:\n" + "\n".join(invalid_list)
        self.client_sock.send_multipart([ADD_TRANS, pickle.dumps(trans_list)])    
        add_trans_response = self.client_sock.recv_multipart()
        return pickle.loads(add_trans_response[1])

    def run_li_ws(self):
        """
        Function to run the web-server.
        """
        app = Flask(__name__)
        CORS(app)
        app.add_url_rule(GET_BLOCKCHAIN_ROUTE, 'get_blockchain', self.get_blockchain, methods = ['GET'])
        app.add_url_rule(GET_UNADDED_TRANS_ROUTE , 'get_unadded_trans', self.get_unadded_trans, methods = ['GET'])
        app.add_url_rule(ADD_TRANS_ROUTE, 'add_trans', self.add_trans, methods = ['POST'])
        log_info(logging, f"Starting local interface node web-server http://127.0.0.0:{self.server_port}.")
        log_info(logging, f"Use the 'local_interface_client.html' file to interface with the node.")
        app.run(port=self.server_port)
