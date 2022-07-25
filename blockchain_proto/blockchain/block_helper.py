"""
Copyright 2022, M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Miscellaneous functions for creating blocks.
"""
from collections import OrderedDict
from datetime import datetime
from typing import List
from blockchain_proto.blockchain.puzzle import sha_256_hash_string, solve_puzzle, check_solution
from blockchain_proto.transactions.transaction import Transaction
from blockchain_proto.blockchain.block_simple import BlockHeader, BlockSimple



def create_block_hash(trans_hash: str,
                      prev_block_hash: str,
                      timestamp: datetime,
                      difficulty: int,
                      nonce: str) -> str:
    """
    Creates a block hash from the information contained in a block header

    Parameters
    ----------
    trans_hash: str
        A hash representing all the transactions that will go into the block.

    prev_block_hash: str
        Hash of the previous block.

    timestamp: datetime
        The timestamp of the creation of the block.

    difficulty: int
        The difficulty level of the puzzle that has been solved.

    nonce: str
        The solution to the puzzle.

    Returns
    -------

    str:
        The block hash created using SHA256.
    """
    block_data_string = "".join([trans_hash,
                                prev_block_hash,
                                str(timestamp),
                                str(difficulty),
                                nonce])
    return sha_256_hash_string(block_data_string)


def solve_block_puzzle(trans_hash: str,
                       prev_block_hash: str,
                       timestamp: datetime,
                       difficulty: int) -> str:
    """
    Solves a crypotgraphic puzzle for the given block information
    at the given difficulty level.

    Parameters
    ----------
    trans_hash: str
        A hash representing all the transactions that will go into the block.

    prev_block_hash: str
        Hash of the previous block.

    timestamp: datetime
        The timestamp of the creation of the block.

    difficulty: int
        The difficulty level of the puzzle that has been solved.

    Returns
    -------

    str:
        The solution to the puzzle.
    """
    puzzle_string = "".join([trans_hash,
                             prev_block_hash,
                             str(timestamp),
                             str(difficulty)])
    return str(solve_puzzle(puzzle_string, difficulty))


def create_block(transactions: List[Transaction],
                 prev_block_hash: str,
                 difficulty: int) -> BlockSimple:

    trans_hash = Transaction.get_trans_hash(transactions)
    timestamp = datetime.now()
    nonce = solve_block_puzzle(trans_hash,
                               prev_block_hash,
                               timestamp,
                               difficulty)
    block_hash = create_block_hash(trans_hash,
                                   prev_block_hash,
                                   timestamp,
                                   difficulty,
                                   nonce)
    new_block_header = BlockHeader(
        block_hash=block_hash,
        transactions_hash=trans_hash,
        prev_block_hash=prev_block_hash,
        timestamp=timestamp,
        difficulty=difficulty,
        nonce=nonce
        )

    return BlockSimple(new_block_header, transactions)


def validate_block_hashes(block: BlockSimple):
    """
    Makes sure that the block puzzle was solved correctly.
    """
    trans_hash = Transaction.get_trans_hash(block.transactions)
    puzzle_string = "".join([trans_hash,
                             block.block_header.prev_block_hash,
                             str(block.block_header.timestamp),
                             str(block.block_header.difficulty)])
    block_hash = create_block_hash(trans_hash,
                                   block.block_header.prev_block_hash,
                                   block.block_header.timestamp,
                                   block.block_header.difficulty,
                                   block.block_header.nonce)
    if block_hash != block.block_header.block_hash:
        raise ValueError(f"Invalid block: block-hash in block header is {block.block_header.block_hash}"
                         f" block hash calculated is {block_hash}.")

    if not check_solution(puzzle_string, block.block_header.nonce, block.block_header.difficulty):
        raise ValueError(f"Invalid block: invalid puzzle solution {block.block_header.nonce}"
                         f" for puzzle {puzzle_string} at difficulty {block.block_header.difficulty}.")
    
    return True


class BlockMap:
    """
    Simple utility class that wraps around a dictionary
    to support storing blocks by their headers.
    """

    def __init__(self):
        self.map = {}

    def __getitem__(self, bhash):
        return self.map[bhash]

    def __contains__(self, bhash):
        return bhash in self.map

    def __len__(self):
        return len(self.map)

    def add(self, block):
        self.map[block.hash()] = block

    def remove(self, bhash):
        del self.map[bhash]

    def get_blocks(self, timestamp):
        if timestamp is None: 
            return list(self.map.values())
        else:
            return [block for block in self.map.values() 
                        if block.block_header.timestamp > timestamp]

    def to_json(self, timestamp=None):
        if timestamp is None: 
            return {block_hash: block.to_json() for block_hash, block in self.map.items()}
        else:
            return {block_hash: block.to_json() for block_hash, block in self.map.items()
                if block.block_header.timestamp > timestamp
            }



