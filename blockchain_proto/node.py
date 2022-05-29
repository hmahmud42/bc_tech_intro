import pickle
import threading
import zmq
import argparse

from blockchain_proto.consts import TRANS_GOSSIP, BLOCK_GOSSIP, \
    INTERFACE_MSG_TYPE, GET_ALL, GET_BLOCK, GET_TRANS_NOT_ADDED, TIMESTAMP_BOUND
from blockchain_proto.blockchain_ds import BlockChain
from blockchain_proto.local_web_server import run_webserver


class Node(object):
    """
    Implements a node in the blockchain.
    """
    def __init__(self, args, context):
        self.args = args
        self.context = context
        self.registry_address = args.registry_address
        self.publish_address = f"tcp://*:{args.port}"
        self.new_node_online_address = f"tcp://*:{args.port + 1}"

        self.local_interface_router = context.socket(zmq.ROUTER)
        self.local_interface_router.bind(f"inproc://local_interface")

        self.gossip_send_socket = context.socket(zmq.PUB)
        self.gossip_send_socket.bind(self.publish_address)

        self.node_response_socket = context.socket(zmq.ROUTER)
        self.node_response_socket.bind(self.publish_address)

        self.gossip_receive_socket = context.socket(zmq.SUBSCRIBE)
        self.gossip_receive_socket.setsockopt(zmq.SUBSCRIBE, TRANS_GOSSIP)
        self.gossip_receive_socket.setsockopt(zmq.SUBSCRIBE, BLOCK_GOSSIP)

        self.peers_info = None

        self.bc = BlockChain(args.trans_per_block, args.difficulty)
        self.add_self_to_registry()

    def add_self_to_registry(self):
        """
        Adds this node to the registry running at the supplied address,
        and retrieves the addresses of the peers that registered with
        the registry, notifies them of this node has come on line.

        IDEA: may be poll the registry to update itself - or have the registry
        refresh its peer directory by polling the nodes.
        """
        register_socket = self.context.socket(zmq.DEALER)
        last_address = self.registry_address
        register_socket.connect(last_address)
        self_info = {
            'publish_address': self.publish_address,
            'new_node_online_address': self.new_node_online_address
        }
        self.peers_info = register_socket.send_json(self_info)

        for peer in self.peers_info:
            register_socket.disconnect(last_address)
            last_address = peer['new_node_online_address']
            register_socket.connect(last_address)
            register_socket.send(bytes(self.publish_address, 'utf-8'))

        register_socket.disconnect(last_address)
        register_socket.close()

    def run_bc_server(self):
        """
        Runs the blockchain server by handling messages from the local
        interface, direct messages from other nodes and messages
        gossiped from other nodes.
        """
        poller = zmq.Poller()
        poller.register(self.local_interface_router, zmq.POLLIN)
        poller.register(self.node_response_socket, zmq.POLLIN)
        poller.register(self.gossip_receive_socket, zmq.POLLIN)

        # Process messages from both sockets
        while True:
            try:
                socks = dict(poller.poll())
            except KeyboardInterrupt:
                break

            if self.local_interface_router in socks:
                self.handle_local_interface_request(self.local_interface_router.recv_json())

            if self.node_response_socket in socks:
                self.handle_new_node_online(self.node_response_socket.recv_multipart())

            if self.gossip_receive_socket in socks:
                self.handle_gossiped_message(self.gossip_receive_socket.recv_multipart())

    def handle_new_node_online(self, msg: [bytes]) -> None:
        """
        Handles the coming of a new node online by sending subscribing to it.

        Parameters
        ----------

        msg: [bytes]
            The message from the new node, with msg[2] containng the ip
            address of the node.
        """
        try:
            msg = self.node_response_socket.recv_multipart()
            self.gossip_send_socket.connect(msg[2].decode('utf-8'))
        except Exception as e:
            print(e)
            print(f"Message Received: {msg}")

    def gossip_object(self, obj_type: bytes, obj: object) -> None:
        """
        Gossips a pickle-serialized version of the the object using
        the

        Parameters
        ----------

        obj_type: bytes
            The object type specified in bytes

        obj: object
            The object to serialize and send
        """
        self.gossip_send_socket.send_multipart([obj_type, pickle.dumps(obj)])

    def handle_local_interface_request(self, json_msg):
        if json_msg[INTERFACE_MSG_TYPE] == GET_ALL:
            return self.bc.to_json()

        if json_msg[INTERFACE_MSG_TYPE] == GET_BLOCK:
            return self.bc.get_blocks_newer(json_msg[TIMESTAMP_BOUND])

        if json_msg[INTERFACE_MSG_TYPE] == GET_TRANS_NOT_ADDED:
            return self.bc.get_trans_not_added(json_msg[TIMESTAMP_BOUND])

    def handle_gossiped_message(self, msg):

        if msg[0] == TRANS_GOSSIP:
            trans = pickle.loads(msg[1])
            try:
                blocks_added = self.bc.add_transaction(trans)
                self.gossip_object(TRANS_GOSSIP, pickle.dumps(trans))
                if blocks_added is not None:
                    for block in blocks_added:
                        self.gossip_object(BLOCK_GOSSIP, pickle.dumps(block))
            except ValueError as v:
                # This means transaction was previously added - so do nothing
                pass

        elif msg[0] == BLOCK_GOSSIP:
            block = pickle.load(msg[1])
            try:
                self.bc.add_incoming_block(block)
                self.gossip_object(BLOCK_GOSSIP, pickle.dumps(block))
            except ValueError as v:
                # This means block was previously added
                pass


def parseargs():
    parser = argparse.ArgumentParser(description='Runs a Blockchain node.')
    parser.add_argument('--registry-address',
                        help='address of where the registry service is running.',
                        required=True
                        )
    parser.add_argument('--port',
                        help='port where the blockchain node will listen.',
                        required=True
                        )
    parser.add_argument('--web-interface-port',
                        help='port where the web interface will be run from.',
                        required=True
                        )
    parser.add_argument('--trans-per-block',
                        help='Number of transactions allowed per block in the chain.',
                        default=10,
                        required=False
                        )
    parser.add_argument('--difficulty',
                        help='Difficulty level for the puzzles in the blockchain.',
                        difficulty=2,
                        required=True
                        )
    return parser.parse_args()


def run():
    args = parseargs()
    context = zmq.Context()
    node = Node(args, context)
    threading.Thread(target=lambda: node.run_bc_server()).start()
    threading.Thread(target=lambda: run_webserver(args, context)).start()


if __name__ == "__main__":
    run()
