"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Implements a node in the blockchain.
"""
from typing import List, Tuple
import pickle, threading, zmq, argparse, random, time, logging
import numpy as np
from datetime import datetime
from dateutil.parser import parse

import blockchain_proto.setup_logger
from blockchain_proto.messages import log_debug, log_info, log_error, log_warning
from blockchain_proto.consts import TRANS_GOSSIP, BLOCK_GOSSIP, \
        GET_BLOCKCHAIN, GET_UNADDED_TRANS, ADD_TRANS, NEW_PEER, BLOCKS_AND_TRANS, \
        node_id_global
from blockchain_proto.blockchain.blockchain_ds import BlockChain
# from blockchain_proto.local_web_server import run_webserver
from blockchain_proto.blockchain.puzzle import sha_256_hash_string
from blockchain_proto.transactions.transaction import Transaction


class Node:
    """
    Class representing a peer in a blockchain.
    """
    def __init__(self, args, context):
        node_id_global['value'] = f"Node {args.node_id}"
        self.id = args.id
        self.context = context
        self.gossip_out_port = args.port
        self.new_peer_notify_port = args.port_new_peer
        self.registry_address = args.registry_address
        
        self.gossip_out_socket = context.socket(zmq.PUB)
        self.gossip_in_socket = context.socket(zmq.SUB)
        self.special_requests_socket = context.socket(zmq.ROUTER)
        self.registry_socket = context.socket(zmq.DEALER)
        self.local_interface_socket = context.socket(zmq.ROUTER)

        self.gossip_in_socket.setsockopt_string(zmq.SUBSCRIBE, 'DATA') 

        self.gossip_out_address = f"tcp://*:{self.gossip_out_port}".encode()
        self.gossip_out_public_address = f"tcp://localhost:{self.gossip_out_port}".encode()
        self.new_peer_notify_address = f"tcp://*:{self.new_peer_notify_port}".encode()
        self.new_peer_notify_public_address = f"tcp://localhost:{self.new_peer_notify_port}".encode()
    
        self.peer_address_list = []
        self.peer_notify_address_list = []
        self.data_received = []

        self.blockchain = BlockChain(args.trans_per_block, args.difficulty)

        self.initialize()

    def initialize(self): 
        """
        Initialize the sockets by binding and connecting them,
        register this peer with the registry service, and connect
        to peers.
        """
        self.registry_socket.connect(f"tcp://{self.registry_address}")
        self.gossip_out_socket.bind(self.gossip_out_address)
        self.local_interface_socket.bind(f"inproc://local_interface")
        self.special_requests_socket.bind(self.new_peer_notify_address)
        self.peer_address_list, self.peer_notify_address_list = self.register()
        self.connect_to_peers()
        self.send_iam_online()

    def register(self) -> Tuple[List[str], List[str]]:
        """
        Registers this node with the registration service, and 
        returns the list of addresses of peers and the address of 
        the publish address of the registry service.

        Returns
        -------

        (list str, list str):
            The list of addresses of peers and the address of the , 
            publish endpoint of the registry service.
        """
        log_info(logging, f"Registering node with registry at: {self.registry_address}")
        self.registry_socket.send_multipart([self.gossip_out_public_address, self.new_peer_notify_public_address])
        registration_reply = self.registry_socket.recv_multipart()
        log_debug(logging, str(registration_reply))

        # get the address of other peers
        peer_address_list = list(set(pickle.loads(registration_reply[1])))
        log_info(logging, f"Received address list {peer_address_list}")
        if self.gossip_out_public_address in peer_address_list:
            peer_address_list.remove(self.gossip_out_public_address)

        # get the notification address of the other peers
        peer_notify_address_list = list(set(pickle.loads(registration_reply[2])))
        log_info(logging, f"Received new peer notify address list {peer_notify_address_list}")
        if self.new_peer_notify_public_address in peer_notify_address_list:
            peer_notify_address_list.remove(self.new_peer_notify_public_address)

        return [pa.decode() for pa in peer_address_list], [pna.decode() for pna in peer_notify_address_list]

    def connect_to_peers(self):
        """
        Connects to the peer in self.peer_address_list
        """
        for peer_address in self.peer_address_list:
            log_info(logging, f"Connecting to peer {peer_address}")
            self.gossip_in_socket.connect(peer_address)
            
    def send_iam_online(self):
        """
        Notifies peers that is online and it should start receiving messages.
        """
        log_info(logging, "Notifying peers that \"I'm online\".")
        notify_socket = self.context.socket(zmq.DEALER)
        for peer_notify_address in self.peer_notify_address_list:
            log_info(logging, f"Sending I am online to {peer_notify_address}")
            notify_socket.connect(peer_notify_address)
            notify_socket.send_multipart([NEW_PEER, self.gossip_out_public_address, self.new_peer_notify_public_address])

        log_info(logging, "Done notifying peers.")

    def handle_gossip_in(self, data: List[bytes]):
        """
        Method to handle the data that was gossiped in.

        Parameters
        ----------

        data: list bytes
            The data recieved from the gossip_in_socket. The first
            element determines the type of the data, the second
            element gives a pickled object of the given type.
        """
        try:
            if data[0] == TRANS_GOSSIP:
                trans = pickle.loads(data[1])
                log_info(logging, f"Adding transaction... {str(trans)}")
                self.blockchain.add_transaction(trans)
            elif data[1] == BLOCK_GOSSIP: 
                    self.blockchain.add_incoming_block(pickle.loads(data[1]))
            else:
                log_error(logging, f"Unknown gossip message type {data[0]}")
        except Exception as e:
            log_error(logging, "When trying to handle gossiped-in message encountered: {e}")

    def handle_local_interface_request(self, request: List[bytes]):
        """
        Method to handle information received from the local
        interface socket. The first element contains the socket
        address where the web server is listening, the second element
        contains the type of the request, and the third any additional
        data.

        Parameters
        ----------

        request: list of bytes
            The request received from the local_interface_socket.
            The second element gives the type of information requested.
        """
        if request[1] == GET_BLOCKCHAIN:
            bc_json = self.blockchain.to_json()
            self.local_interface_socket.send_multipart(
                [request[0], b'', pickle.dumps(bc_json)]
            )

        elif request[1] == GET_UNADDED_TRANS:
            trans = self.blockchain.get_trans_not_added_json()
            log_info(logging, f"Returning Un-added transactions {trans}.")
            self.local_interface_socket.send_multipart(
                [request[0], b'', pickle.dumps(trans)]
            )

        elif request[1] == ADD_TRANS:
            trans = pickle.loads(request[2])
            log_info(logging, f"Adding transaction... {str(trans)}")
            self.blockchain.add_transaction(trans)
            self.local_interface_socket.send_multipart(
                [request[0], b'', request[2]]
            )
        else:
            log_warning(logging, f"Unknown request {request[1]} via the local interface.")
        

    def add_blocks_trans(self, request: List[bytes]):
        """
        Adds blocks and transactions received from a new peer that has just connected.

        request: list of bytes
            Data recevied from the peer.
        """
        blocks_trans = pickle.loads(request[2])
        log_info(logging, f"Adding {len(blocks_trans[0])} blocks from peer.")
        for block in blocks_trans[0]:
            self.blockchain.add_incoming_block(block)
        log_info(logging, f"Adding {len(blocks_trans[1])} transactions from peer.")
        for trans in blocks_trans[1]:
            self.blockchain.add_transaction(trans)

    def handle_new_peer(self, new_peer_info: List[bytes]):
        """
        Method to handle a new peer.

        Parameters
        ----------

        new_peer_info: list of bytes
            The data recieved from the gossip_in_socket
        """
        self.peer_address_list.append(new_peer_info[2].decode())
        self.peer_notify_address_list.append(new_peer_info[3].decode())

        self.gossip_in_socket.connect(self.peer_address_list[-1])
        send_blocks_trans_socket = self.context.socket(zmq.DEALER   )
        send_blocks_trans_socket.connect(self.peer_notify_address_list[-1])
        data = pickle.dumps( [self.blockchain.get_block_list(), self.blockchain.get_trans_not_added()])
        send_blocks_trans_socket.send_multipart([BLOCKS_AND_TRANS, data])

        log_info(logging, f"Connected to new peer that has come online {self.peer_address_list[-1]} and sent it my blocks/trans.")

    def run(self):
        """
        Runs the main loop for the node to get data from the data
        generation process, and gossip it out to existing peers,
        get data generated by other peers and get addresses of new
        peers who register with the registry service.
        """
        poller = zmq.Poller()
        poller.register(self.local_interface_socket, zmq.POLLIN)
        poller.register(self.gossip_in_socket, zmq.POLLIN)
        poller.register(self.special_requests_socket, zmq.POLLIN)

        log_info(logging, "**** Hello There! ****")
        log_info(logging, "Local BC-Proto node is now running...")
        log_info(logging, f"Port: {self.gossip_out_port}, " + 
                          f"New-Peer-Port: {self.new_peer_notify_port}, " +
                          f"Using registry at: {self.registry_address}")

        while True:
            socks = dict(poller.poll())

            if self.gossip_in_socket in socks:
                data = self.gossip_in_socket.recv_multipart()
                self.handle_gossip_in(data)

            if self.local_interface_socket in socks:
                log_info(logging, "Local interface request recevied")
                request = self.local_interface_socket.recv_multipart()
                self.handle_local_interface_request(request)

            if self.special_requests_socket in socks:
                request = self.special_requests_socket.recv_multipart()
                if request[1] == NEW_PEER:
                    self.handle_new_peer(request)
                elif request[1] == BLOCKS_AND_TRANS:
                    self.add_blocks_trans(request)
                else:
                    log_error(logging, f"Unknown message type in additional_request socket: {request[1]}")


def parseargs():
    """
    Parse the arguments.
    """
    parser = argparse.ArgumentParser(description='Runs a Proto-blockchain node.')
    parser.add_argument('--port',
                        help="Port where the node will listen for incoming"+
                            "messages from peers.",
                        required=True)
    parser.add_argument('--port-new-peer',
                        help="Port where the node will listen for new peers",
                        required=True)
    parser.add_argument('--registry-address',
                        help='Address of where the registry service is running.' +
                        "must of the form 'host-ip:port'",
                        required=True)
    parser.add_argument('--trans-per-block',
                        help='Number of transactions allowed per block in the chain.',
                        default=10, type=int, required=False)
    parser.add_argument('--difficulty',
                        help='Difficulty level for the puzzles in the blockchain.',
                        default=2, type=int, required=False)
    parser.add_argument('--user-id',
                        help='User id for test.',
                        default=1, type=int, required=False)
    parser.add_argument('--node-id',
                        help="ID of node - used only for displaying messages.",
                        default=1,                            
                        required=False)


    return parser.parse_args()



def create_transactions_2(user_nums, base_trans, trans_per_user):
    """
    Create the transactions according to the given parameters.

    Parameters
    ----------

    user_nums: list of int
        The id-number of the users in the transaction

    base_trans: list of int
        The starting point of the different transactions.

    trans_per_user: list of int
        The number of transactions per user.
    """
    tr_list = []
    other_users = ['Bikash', 'Jamila', 'Asha', 'Xinping']
    for i, num in enumerate(user_nums):
        for t in range(trans_per_user[i]):
            coins = np.random.randint(low=22, high=44)
            user = np.random.choice(other_users)
            tr = Transaction(user_id=f"User {num}",
                        trans_no=base_trans[i] + t,
                        trans_str=f"Pay {user} {coins} Gold coins")
            tr_list.append(tr)

    return tr_list


def test_local(context, user_id):
    local_interface_socket = context.socket(zmq.DEALER)
    local_interface_socket.connect(f"inproc://local_interface")
    trans = create_transactions_2([user_id], [0], [10])
    for tran in trans:
        local_interface_socket.send_multipart([
            ADD_TRANS, pickle.dumps(tran)])
        local_interface_socket.recv_multipart()
    
    local_interface_socket.send_multipart([GET_UNADDED_TRANS])
    unadded_trans = local_interface_socket.recv_multipart()
    
    log_debug(logging, f"Transactions not yet added: {pickle.loads(unadded_trans[1])}")


def run():
    args = parseargs()
    context = zmq.Context()
    setattr(args, "id", sha_256_hash_string(str(datetime.now) + str(random.randint(0, 10000))))
    node = Node(context=context, args=args)
    threading.Thread(target=lambda: node.run()).start()
    # threading.Thread(target=lambda: run_webserver(args.web_interface_port, 
    #                                               context)).start()
    threading.Thread(target=lambda: test_local(context, args.user_id)).start()


if __name__ == "__main__":
    run()
