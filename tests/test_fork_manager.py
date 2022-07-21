"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Tests the fork manager.
"""
from datetime import datetime

from blockchain_proto.block_creator import create_block
from blockchain_proto.transaction import Transaction
from blockchain_proto.block_simple import BlockHeader, BlockSimple
from blockchain_proto.fork_manager import  ForkManager
from blockchain_proto.consts import NULL_BLOCK_HASH
from block_creator_for_test import create_transactions
from blockchain_proto.messages import unordered_trans_msg, prec_block_not_found_msg, \
    earliest_trans_mismatch_msg, block_was_already_added_msg



def create_block_header():
    return BlockHeader(
        block_hash="block_hash",
        transactions_hash="trans_hashes",
        prev_block_hash=NULL_BLOCK_HASH,
        timestamp=datetime.now(),
        difficulty=3,
        nonce="1")


def create_block_simple(base_trans):
    bh = create_block_header()
    trans_list = list(create_transactions(base_trans))
    return BlockSimple(block_header=bh, transactions=trans_list)


def test_fork_manager_add():

    fork_manager = ForkManager()
    # number of forks including main branch.
    num_forks = 6
    main_branch_len = 10
    # block at which forks will enter the main branch
    # main branch index is 0 - blocks counted from 0
    fork_entry_points = [3, 4, 5, 6, 7]
    # additional number of blocks to be added to each fork
    # so fork number 2 will have length 5 + 7 = 12
    # and should be the longest fork at end.
    fork_lens = [6, 7, 3, 2, 1]

    # create main branch
    base_trans = [0, 0]
    prev_hash = NULL_BLOCK_HASH
    block_list = []
    for i in range(main_branch_len):
        trans = create_transactions(base_trans)
        block = create_block(trans, prev_hash, 1)
        fork_manager.add_blocks([block])
        base_trans [0] += 3
        base_trans [1] += 1
        prev_hash = block.block_header.block_hash
        block_list.append(block)
    
    base_transes = [[(fep+1)*3, fep+1] for fep in fork_entry_points]

    # create the forks
    for fj, fep in enumerate(fork_entry_points):
        prev_hash = block_list[fep].block_header.block_hash
        base_trans = base_transes[fj]
        for i in range(fork_lens[fj]):
            trans = create_transactions(base_trans)
            block = create_block(trans, prev_hash, 1)
            fork_manager.add_blocks([block])            
            base_trans [0] += 3
            base_trans [1] += 1
            prev_hash = block.block_header.block_hash
            block_list.append(block)

    # # now check the validity 
    assert fork_manager.next_fork_id == num_forks
    assert len(fork_manager.forks) == num_forks

    for fork_id in range(1, num_forks):
        assert fork_manager.forks[fork_id].num_blocks == \
            (fork_entry_points[fork_id-1] + fork_lens[fork_id-1] + 1)

    assert fork_manager.get_longest_fork().fork_id == 2    

    # Test error condition: block was already added
    ret = fork_manager.add_blocks([block])
    error_msg = block_was_already_added_msg(block.hash())
    assert ret[0] == error_msg
    
    # Test error condition transaction ordering
    base_trans[0] = block.transactions[2].trans_no
    base_trans[1] = block.transactions[3].trans_no
    trans = create_transactions(base_trans)
    prev_hash = block_list[-1].hash()
    block = create_block(trans, prev_hash, 1)
    ret = fork_manager.add_blocks([block])
    error_msg = earliest_trans_mismatch_msg("User 1", block.hash(), 
                    base_trans[0], base_trans[0])
    assert ret[0] == error_msg

    # Test prec block not found 
    bad_prev_hash =  "RANDOM_HASH"
    block = create_block(trans, bad_prev_hash, 1)
    ret = fork_manager.add_blocks([block])
    error_msg = prec_block_not_found_msg(block.hash(), bad_prev_hash)
    assert ret[0] == error_msg  

    # test unordered transaction message
    base_trans[0] = block.transactions[2].trans_no + 1
    base_trans[1] = block.transactions[3].trans_no + 1
    trans = list(create_transactions(base_trans))
    trans[0], trans[1] = trans[1], trans[0]
    block = create_block(trans, prev_hash, 1)
    ret = fork_manager.add_blocks([block])
    error_msg = unordered_trans_msg("User 1", block.hash())
    assert ret[0] == error_msg


if __name__ == '__main__':
    test_fork_manager_add()




