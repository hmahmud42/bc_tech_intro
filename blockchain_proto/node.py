import pickle
import threading
import zmq
import argparse


TRANS_GOS = b'transaction'
BLOCK_GOS = b'block'

class LocalNode(object):
    """
    Implements a local node.
    """

    def __init__(self, args, context):
        self.args = args
        self.context = context

        self.local_interface_router = context.socket(zmq.ROUTER)
        self.local_interface_router.bind(f"inproc://local_interface")

        self.node_response_socket = context.socket(zmq.ROUTER)
        self.node_response_socket.bind(f"tcp://*:{args.port + 1}")

        self.gossip_receive_socket = context.socket(zmq.SUBSCRIBE)
        self.gossip_receive_socket.setsockopt(zmq.SUBSCRIBE, TRANS_GOS)
        self.gossip_receive_socket.setsockopt(zmq.SUBSCRIBE, BLOCK_GOS)

        self.gossip_receive_socket.bind(f"tcp://*:{args.port + 2}")

        self.gossip_send_socket = context.socket(zmq.PUB)
        self.gossip_send_socket.bind(f"tcp://*:{args.port + 3}")

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
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--port', help='port where the blockchain node will listen', required=True)
    parser.add_argument('--web-interface-port', help='port where the web interface will be run from', required=True)
    args = parser.parse_args()


def run()
    args = parseargs()
    context = zmq.Context()
    threading.Thread(target=lambda: run_bc_server(args, context)).start()
    threading.Thread(target=lambda: run_webserver(args, context)).start()
    # threading.Thread(target=lambda: serve(app, host=host_name, port=port)).start()


if __name__ == "__main__":
    run()
