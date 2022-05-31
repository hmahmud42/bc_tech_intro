"""
Implements a simple blockchain data structure.
"""
from typing import Union

from blockchain_proto.block_simple import BlockSimple
from blockchain_proto.transaction import Transaction, TransactionManager
from blockchain_proto.fork_manager import ForkManager, Fork
from blockchain_proto.block_creator import create_block
from blockchain_proto.consts import *


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

    def add_transaction(self, transaction: Transaction) -> [BlockSimple]:
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
        if len(self.trans_dict) < self.trans_per_block: return []
        self.cleanup()
        longest_fork = self.fork_manager.longest_fork()
        valid_trans = self.trans_manager.get_valid_trans(longest_fork.user_trans_dict if longest_fork else {})
        if len(valid_trans) < self.trans_per_block: return []
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
        return {
            TRANS_PER_BLOCK: self.trans_per_block,
            DIFFICULTY: self.difficulty,
            BLOCK_MAP: {block_hash: block.to_json() for block_hash, block in self.block_map.items()},
            TRANS_DATA: self.trans_manager.to_json(),
            FORK_DATA: self.fork_manager.to_json()
        }

    def get_blocks_newer_json(self, timestamp):
        """
        Returns blockchains which are newer than the given timestamp.
        """
        return {
            block_hash: block.to_json() for block_hash, block in self.block_map.items()
                        if block.block_header.timestamp >= timestamp

        }

    def get_trans_not_added_json(self):
        """
        Returns transactions which have not been added so far.
        """
        return self.trans_manager.to_json()
