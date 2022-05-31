from datetime import datetime

from blockchain_proto.consts import BLOCK_HASH, TRANS_HASH, PREV_BLOCK_HASH, TIMESTAMP, DIFF, NONCE, BLOCK_HEADER, \
    BLOCK_TRANS
from blockchain_proto.transaction import Transaction


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

    def to_json(self):
        """
        Returns json version of this BlockHeader

        Returns
        -------
        dict:
            json representation of the the block-header
        """
        return {
            BLOCK_HASH: self.block_hash,
            TRANS_HASH: self.transactions_hash,
            PREV_BLOCK_HASH: self.prev_block_hash,
            TIMESTAMP: self.timestamp,
            DIFF: self.difficulty,
            NONCE: self.nonce
        }


class BlockSimple(object):

    def __init__(self,
                 block_header: BlockHeader,
                 transactions: [Transaction]) -> None:
        self.block_header = block_header
        self.transactions = transactions

    def to_json(self):
        """
        Returns json version of this BlockSimple

        Returns
        -------
        dict:
            json representation of the the block
        """
        return {
            BLOCK_HEADER: self.block_header.to_json(),
            BLOCK_TRANS: [trans.to_json() for trans in self.transactions]
        }