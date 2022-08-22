"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Implements the registry service in the blockchain.
"""
import zmq, pickle, argparse, setup_logger, logging
from blockchain_proto.messages import log_info
from blockchain_proto.consts import node_id_global


def run(registry_port=5001):

    node_id_global['value'] = 'Registry'    
    log_info(logging, f"Starting proto-blockchain registry listening at {registry_port}.")

    context = zmq.Context()

    #  Socket for first connection 
    registry_socket = context.socket(zmq.ROUTER)
    registry_socket.bind(f"tcp://*:{registry_port}")

    address_list = []
    notify_address_list = []

    while True:
        # Socket to send messages out to other nodes
        message = registry_socket.recv_multipart()
        log_info(logging, f"New peer connected at: {message[1]}.")
        log_info(logging, f"Sending new peer registry info.")
        registry_socket.send_multipart([message[0], b'', 
                                        pickle.dumps(address_list), 
                                        pickle.dumps(notify_address_list)])

        if message[1] not in address_list:
            address_list.append(message[1])

        if message[2] not in notify_address_list:
            notify_address_list.append(message[2])


def parseargs():
    """
    Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Runs a Blockchain node.')
    parser.add_argument('--port',
                        help="Port where the registry will listen for for new ndoes.",
                        type=int,
                        required=True)
    return parser.parse_args()



if __name__ == '__main__':
    args = parseargs()
    run(args.port)
