"""
Copyright 2022, M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Utility functions for creating blocks
"""
from blockchain_proto.transaction import Transaction
from blockchain_proto.block_creator import create_block


def create_transactions(base_trans):
    tr1 = Transaction(user_id="User 1",
                      trans_no=base_trans[0],
                      trans_str="Pay Bob 23 Gold coins")
    # test ordering
    tr2 = Transaction(user_id="User 1",
                      trans_no=base_trans[0]+1,
                      trans_str="Pay Bob 23 Gold coins")
    tr3 = Transaction(user_id="User 1",
                      trans_no=base_trans[0]+2,
                      trans_str="Pay Bob 23 Gold coins")
    tr4 = Transaction(user_id="User 2",
                      trans_no=base_trans[1],
                      trans_str="Pay Bob 23 Gold coins")

    return tr1, tr2, tr3, tr4

