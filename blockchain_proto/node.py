import pickle
import threading
import zmq
import argparse
from blockchain_proto.fork_manager import AuthManager
from blockchain_proto.transaction import TransactionManager


TRANS_GOS = b'transaction'
BLOCK_GOS = b'block'


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
        self.gossip_receive_socket.setsockopt(zmq.SUBSCRIBE, TRANS_GOS)
        self.gossip_receive_socket.setsockopt(zmq.SUBSCRIBE, BLOCK_GOS)

        self.peers_info = None

        self.auth_manager = AuthManager()
        self.bc = Blockchain(args.trans_per_block, args.difficulty)
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

        if json_msg['type'] == GET_LATEST_BLOCK:



        # get message type
        # new transaction for user
        # if transaciton number is fine, accept it
        # return transaction
        # accepted
        # gossip
        # transaction
        # # get current blockchain
        # return json
        # version
        # of
        # current
        # chain

    def handle_gossiped_message(self, msg):

        if msg[0] == b'transaction':
            trans = pickle.loads(msg[1])
            self.auth_manager.validate_incoming_transaction(trans)
            self.bc.add_transaction(trans)

        elif msg[0] == b'block':
            block = pickl.load(msg[1])
            self.bc.add_block()

        # if message type is transaciton
        # add_transaction
        # gossip
        # transaciton
        # if transaction added,
        # gosip
        # transaction

        # if message type is block:
            # validate and add
            # blcok
            # if block added
            # gossip
            # block


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
    threading.Thread(target=lambda: run_bc_server(args, context)).start()
    threading.Thread(target=lambda: run_webserver(args, context)).start()
    # threading.Thread(target=lambda: serve(app, host=host_name, port=port)).start()


if __name__ == "__main__":
    run()
