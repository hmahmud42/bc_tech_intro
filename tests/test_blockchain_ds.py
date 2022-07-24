"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Tests for the blockchain data structure.
"""
from blockchain_proto.blockchain.block_helper import create_block
from blockchain_proto.blockchain.blockchain_ds import BlockChain
from copy import deepcopy
from block_creator_for_test import create_transactions_2


def test_blockchain_ds():

    user_nums = [1, 2, 3]
    base_trans = [0, 0, 0] 
    trans_per_user = [3, 10, 7]
    trans_list = create_transactions_2(user_nums, base_trans, trans_per_user)
    assert len(trans_list) == 20
    
    trans_per_block = 6
    difficulty = 1
    blockchain = BlockChain(trans_per_block=trans_per_block, difficulty=difficulty)
    for t in trans_list:
        blockchain.add_transaction(t)

    assert len(blockchain.block_map) == 3
    assert blockchain.free_trans_manager.num_free() == 2

    base_trans = deepcopy(trans_per_user)
    trans_per_user = [7, 3, 10]
    trans_list = create_transactions_2(user_nums, base_trans, trans_per_user)
    for t in trans_list:
        blockchain.add_transaction(t)

    assert len(blockchain.block_map) == 6
    assert blockchain.free_trans_manager.num_free() == 4

    # create an incoming block that will create a fork
    blocks = blockchain.get_blocks_newer(None)
    block_middle = blocks[2]
    trans_list = create_transactions_2([1], [3], [7])
    inc_block = create_block(trans_list, block_middle.hash(), 1)
    blockchain.add_incoming_block(inc_block)

    assert len(blockchain.block_map) == 7
    assert blockchain.fork_manager.num_forks() == 2

    # create an incoming block that will absorb the free transactions
    # in the free_transaction_manager
    trans_list = create_transactions_2([3], [13], [6])
    inc_block = create_block(trans_list, blocks[-1].hash(), 1)
    blockchain.add_incoming_block(inc_block)
    assert len(blockchain.block_map) == 8
    assert blockchain.fork_manager.num_forks() == 2
    assert blockchain.free_trans_manager.num_free() == 0




if __name__ == '__main__':
    test_blockchain_ds()
