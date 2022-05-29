"""
Implements a simple blockchain data structure.
"""
from typing import Union
from blockchain_proto.transaction import Transaction, TransactionManager
from datetime import datetime
from blockchain_proto.consts import NULL_BLOCK_HASH
from blockchain_proto.block_creator import *
from blockchain_proto.fork_manager import ForkManager, Fork
from blockchain_proto.consts import *


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
        # self.latest_block_hashes = [] # this is a list - one for each fork.
        self.fork_lengths = []
        self.block_map = {}
        # self.current_transactions = []
        self.trans_dict = {}
        self.trans_manager = TransactionManager()
        self.fork_manager = ForkManager()

    def add_transaction(self, transaction: Transaction) -> Union[[BlockSimple], None]:
        """
        Adds a transaction after validating it, and returns a new block if
        created. If transaction validation fails, it returns the error message (to
        be shown to the user via the portal if running).

        Returns None if no block is created.

        Parameters
        ----------

        transaction: Transaction
            The transaction to add to the block.

        Returns
        -------

        BlockSimple | str | None:
            As described in the function description.
        """
        self.trans_manager.add_transaction(transaction)
        if len(self.trans_dict) < self.trans_per_block: return None
        self.cleanup()
        longest_fork = self.fork_manager.longest_fork()
        valid_trans = self.trans_manager.get_valid_trans(longest_fork.user_trans_dict if longest_fork else {})
        if len(valid_trans) < self.trans_per_block: return None
        return self.add_new_blocks(valid_trans, longest_fork)

    def add_new_blocks(self, valid_trans:[Transaction], fork: Fork) -> [BlockSimple]:
        """
        Create and add new blocks using the valid transactions to the given form.

        Parameters
        ----------
        valid_trans: [Transaction]
            List of transactions to add to the new block(s).
            Assumes that the transactions are ordered by transaction number.

        fork: Fork
            The fork to add the transactions to

        Returns
        -------
        [BlockSimple]:
            All the blocks added
        """
        trans_to_remove = []
        latest_block_hash = fork.block_hash if fork else NULL_BLOCK_HASH
        blocks_added = []
        while len(valid_trans) >= self.trans_per_block:
            new_block = create_block(valid_trans[0:self.trans_per_block],
                                     latest_block_hash,
                                     self.difficulty)
            self.block_map[new_block.block_header.block_hash] = new_block
            latest_block_hash = new_block.block_header.block_hash

            trans_to_remove.append(valid_trans[0:self.trans_per_block])
            valid_trans = valid_trans[self.trans_per_block:]
            blocks_added.append(new_block)

        self.fork_manager.update(fork, blocks_added)
        self.trans_manager.remove_older_and_equal_trans(trans_to_remove)
        return blocks_added

    def add_incoming_block(self, incoming_block: BlockSimple) -> Union[BlockSimple, str]:
        """
        Adds a new block, sent by another peer, to the this blockchain which
        after validating it, and returns the block itself. If validation fails,
        returns an error message.

        Returns None if no block is created.

        Parameters
        ----------

        incoming_block: BlockSimple
            The block to add to the chain.

        Returns
        -------

        BlockSimple | str:
            As described in the function description.
        """
        if incoming_block.block_header.block_hash in self.block_map:
            raise ValueError(f"Block with has {incoming_block.block_header.block_hash} was already added.")
        try:
            fork = self.fork_manager.validate_incoming_block(incoming_block)
        except ValueError as v:
            return str(v)

        self.fork_manager.update(fork, [incoming_block])
        return incoming_block

    def cleanup(self):
        """
        Cleans up the blockchain by removing any fork that has become too
        short compared to the longest fork and moves all its transactions into
        the list of transactions that can be added.
        """
        released_block_hashes = self.fork_manager.cleanup_forks(self.block_map)
        for block_hash in released_block_hashes:
            block = self.block_map[block_hash]
            for trans in block.transactions:
                self.trans_manager.add_transaction(trans)

            del self.block_map[block_hash]

    def to_json(self):
        """
        Returns json version of this BlockChain

        Returns
        -------
        dict:
            json representation of the the block chain.
        """
        pass

    def get_blocks_newer(self, timestamp):
        """
        Returns blockchains which are newer than the given timestamp.
        """
        pass

    def get_trans_not_added(self, timestamp):
        """
        Returns transactions which have not been added so far.
        """
        pass
