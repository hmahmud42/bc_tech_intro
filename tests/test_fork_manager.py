"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Code for managing forks in the chain.
"""
from datetime import datetime

from blockchain_proto.block_creator import create_block
from blockchain_proto.transaction import Transaction
from blockchain_proto.block_simple import BlockHeader, BlockSimple
from blockchain_proto.fork_manager import  ForkManager
from blockchain_proto.consts import NULL_BLOCK_HASH
from block_creator_for_test import create_transactions


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


def test_fork_manager_update():

    # check new fork was created
    # base_trans = [23, 24]
    # bs_1 = create_block_simple(base_trans)    
    # fork_manager = ForkManager()
    # fork_manager.update(None, [bs_1])
    # assert fork_manager.next_fork_id == 1
    # assert fork_manager.fork_hashes[bs_1.block_header.block_hash].fork_id == 1
    # assert fork_manager.forks[1].fork_id == 1
    # assert fork_manager.longest_fork == fork_manager.forks[1]
    # assert fork_manager.longest_fork.user_trans_dict['User 1'] == 25
    # assert fork_manager.longest_fork.user_trans_dict['User 2'] == 24

    # # create another fork
    # base_trans = [26, 25]
    # bs_2 = create_block_simple(base_trans)
    # bs_2.block_header.block_hash = "block_hash_for_second_block"
    # fork_manager.update(None, [bs_2])
    # assert fork_manager.next_fork_id == 2
    # assert fork_manager.fork_hashes[bs_2.block_header.block_hash].fork_id == 2
    # assert fork_manager.forks[2].fork_id == 2
    # assert fork_manager.longest_fork == fork_manager.forks[1]
    # assert fork_manager.forks[2].user_trans_dict['User 1'] == 28
    # assert fork_manager.forks[2].user_trans_dict['User 2'] == 25
    # assert fork_manager.longest_fork.user_trans_dict['User 2'] == 24

    # # add a new block to the second fork
    # base_trans = [29, 26]
    # next_fork = fork_manager.forks[2]
    # bs_3 = create_block_simple(base_trans)
    # bs_3.block_header.block_hash = "block_hash_for_third_block"
    # bs_3.block_header.prev_block_hash = "block_hash_for_second_block"
    # fork_manager.update(next_fork, [bs_3])
    # assert fork_manager.next_fork_id == 2
    # assert fork_manager.fork_hashes[bs_3.block_header.block_hash].fork_id == 2
    # assert fork_manager.forks[2].fork_id == 2
    # assert fork_manager.longest_fork == fork_manager.forks[2]
    # assert fork_manager.longest_fork.user_trans_dict['User 1'] == 31
    # assert fork_manager.longest_fork.user_trans_dict['User 2'] == 26
    # assert len(fork_manager.fork_hashes) == 2

    # create a set number of forks and make sure
    # the correct numbers are created
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
    
    # for i, hash in enumerate(fork_manager.block_depth_manager):
    #     print(f"{i}: {hash}")

    print("\n------\n")
    for i, b in enumerate(block_list):
        print(f"{i}: {b.block_header.block_hash}")
    print("\n------\n")

    base_transes = [[(fep+1)*3, fep+1] for fep in fork_entry_points]
    print(base_transes)


    # create the forks
    for fj, fep in enumerate(fork_entry_points):
        print(f"Creating branch at {fep}")
        prev_hash = block_list[fep].block_header.block_hash
        print(f"prev_hash {prev_hash}")
        base_trans = base_transes[fj]
        for i in range(fork_lens[fj]):
            print(f"block number {i}")
            trans = create_transactions(base_trans)
            block = create_block(trans, prev_hash, 1)
            print(block.block_header.prev_block_hash)
            fork_manager.add_blocks([block])            
            base_trans [0] += 3
            base_trans [1] += 1
            prev_hash = block.block_header.block_hash
            block_list.append(block)

    # # now check the validity 
    # assert fork_manager.next_fork_id == num_forks
    # assert len(fork_manager.forks) == num_forks
    # for fork_id in range(1, num_forks):
    #     assert fork_manager.forks[fork_id].num_blocks == \
    #         fork_entry_points[fork_id] + fork_lens[fork_id]

    # assert fork_manager.longest_fork.fork_id == 2    
    

if __name__ == '__main__':
    test_fork_manager_update()




