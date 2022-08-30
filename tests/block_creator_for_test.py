"""
Copyright 2022, M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Utility functions for creating blocks for tests.
"""
import numpy as np
from blockchain_proto.transactions.transaction import Transaction
from blockchain_proto.blockchain.block_helper import create_block


def create_transactions(base_trans):
    tr1 = Transaction(user_id="User 1",
                      trans_no=base_trans[0],
                      trans_details="Pay Bob 23 Gold coins")
    # test ordering
    tr2 = Transaction(user_id="User 1",
                      trans_no=base_trans[0]+1,
                      trans_details="Pay Bob 23 Gold coins")
    tr3 = Transaction(user_id="User 1",
                      trans_no=base_trans[0]+2,
                      trans_details="Pay Bob 23 Gold coins")
    tr4 = Transaction(user_id="User 2",
                      trans_no=base_trans[1],
                      trans_details="Pay Bob 23 Gold coins")

    return tr1, tr2, tr3, tr4



def create_transactions_2(user_nums, base_trans, trans_per_user):
    """
    Create the transactions according to the given parameters.

    Parameters
    ----------

    user_nums: list of int
        The id-number of the users in the transaction

    base_trans: int
        The starting point of the different transactions.

    trans_per_user: int
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
