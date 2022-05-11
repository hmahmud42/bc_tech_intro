"""
Miscellaneous function for creating blocks.
"""
from datetime import datetime
from blockchain_proto.puzzle import concat_strs, sha_256_hash_string, solve_puzzle
from blockchain_proto.transaction import Transaction
from blockchain_proto.blockchain_ds import BlockSimple, BlockHeader


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
    block_data_string = concat_strs([trans_hash,
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
    puzzle_string = concat_strs([trans_hash,
                                prev_block_hash,
                                str(timestamp),
                                str(difficulty)])
    return str(solve_puzzle(puzzle_string, difficulty))


def create_block(transactions: [Transaction],
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
    new_block_header = BlockHeader(block_hash,
                                    trans_hash,
                                    prev_block_hash,
                                    timestamp,
                                    difficulty,
                                    nonce)

    return BlockSimple(new_block_header, transactions)

