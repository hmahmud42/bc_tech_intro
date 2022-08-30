"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Some simple functions that adds a transaction to the node running in the same process.
"""
import logging
import zmq
import pickle


import numpy as np
from blockchain_proto.transactions.transaction import Transaction
from blockchain_proto.consts import ADD_TRANS, GET_UNADDED_TRANS
from blockchain_proto.messages import log_debug


def create_transactions_for_test(user_nums, base_trans, trans_per_user):
    """
    Create the transactions according to the given parameters for
    running the test

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
                             trans_details=f"Pay {user} {coins} Gold coins")
            tr_list.append(tr)

    return tr_list


def test_local(user_id, context):
    """
    Runs a simple test by adding 10 transactions to the blockchain
    for the given user-id.
    """
    local_interface_socket = context.socket(zmq.DEALER)
    local_interface_socket.connect(f"inproc://local_interface")
    trans = create_transactions_for_test([user_id], [0], [10])
    local_interface_socket.send_multipart([ADD_TRANS, pickle.dumps(trans)])
    local_interface_socket.recv_multipart()
    local_interface_socket.send_multipart([GET_UNADDED_TRANS])
    unadded_trans = local_interface_socket.recv_multipart()
    
    log_debug(logging, f"Transactions not yet added: {pickle.loads(unadded_trans[1])}")

