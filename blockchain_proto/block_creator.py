"""
Copyright 2022, M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Miscellaneous functions for creating blocks.
"""
from datetime import datetime
from typing import List
from blockchain_proto.puzzle import concat_strs, sha_256_hash_string, solve_puzzle, check_solution
from blockchain_proto.transaction import Transaction
from blockchain_proto.block_simple import BlockHeader, BlockSimple


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
