"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Test the creation of blocks.
"""
from blockchain_proto.block_creator import create_block, validate_block_hashes, \
    create_block_hash
from blockchain_proto.transaction import Transaction
from blockchain_proto.puzzle import sha_256_hash_string, check_solution
from tests.block_creator_for_test import  create_transactions


def test_block_creation():
    
    trans = create_transactions([23, 1])

    block = create_block(
        transactions=trans,
        prev_block_hash='test_hash',
        difficulty=1)

    trans_hash = Transaction.get_trans_hash(trans)
    test_hash = sha_256_hash_string("".join([
        trans_hash,
        'test_hash',
        str(block.block_header.timestamp),
        "1",
        block.block_header.nonce])
    )

    assert test_hash == create_block_hash(
        trans_hash, 'test_hash',
        block.block_header.timestamp, 1,
        block.block_header.nonce)

    assert validate_block_hashes(block)

    puzzle_string = "".join(
        [trans_hash, 'test_hash', 
         str(block.block_header.timestamp), "1"])

    assert check_solution(puzzle_string, block.block_header.nonce, 1)



if __name__ == '__main__':
    test_block_creation()


