"""
Implements a simple blockchain data structure.
"""
from blockchain_proto.transaction import Transaction
from datetime import datetime
from blockchain_proto.block_creator import *


class BlockHeader(object):
    def __init__(self,
                 block_hash: str,
                 transactions_hash: str,
                 prev_block_hash: str,
                 timestamp: datetime,
                 difficulty: int,
                 nonce: str) -> None:

        self.block_hash = block_hash
        self.transactions_hash = transactions_hash
        self.prev_block_hash = prev_block_hash
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.nonce = nonce


class BlockSimple(object):

    def __init__(self,
                 block_header: BlockHeader,
                 transactions: [Transaction]) -> None:
        self.block_header = block_header
        self.transactions = transactions


class BlockChain(object):
    """
    Represents a blockchain.

    Parameters
    ----------

    trans_per_block: int
        Number of transactions per block.

    difficulty: int
        The level of difficulty level for the puzzles in the blockchain.
    """
    def __init__(self, trans_per_block: int, difficulty: int) -> None:
        self.trans_per_block = trans_per_block
        self.difficulty = difficulty
        self.latest_block_hash = None
        self.block_hash_to_block_map = {}
        self.current_transactions = []

    def add_transaction(self, transaction: Transaction) -> BlockSimple:
        self.current_transactions.append(transaction)
        if len(self.current_transactions) < self.trans_per_block:
            return None

        new_block = create_block(self.current_transactions,
                                 self.latest_block_hash,
                                 self.difficulty)
        self.block_hash_to_block_map[new_block.block_header.block_hash] = new_block
        self.latest_block_hash = new_block.block_header.block_hash
        self.current_transactions = []
        return new_block
