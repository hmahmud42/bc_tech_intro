"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Implements a simple blockchain data structure.
"""
from os import remove, times
from typing import Union, List
import logging

from blockchain_proto.blockchain.block_simple import BlockSimple
from blockchain_proto.transactions.transaction import Transaction
from blockchain_proto.transactions.free_transaction_manager import FreeTransactionManager
from blockchain_proto.forks.fork import Fork
from blockchain_proto.forks.fork_manager import ForkManager
from blockchain_proto.blockchain.block_helper import create_block, BlockMap
from blockchain_proto.consts import *
from blockchain_proto.exceptions import BlockWasAlreadyAddedError, TransWasAlreadyAddedError
from blockchain_proto.log_messages import log_info, log_debug, log_warning, log_error, log_critical



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
    def __init__(self, trans_per_block: int, difficulty: int):
        self.trans_per_block = trans_per_block
        self.difficulty = difficulty
        self.block_map = BlockMap()
        self.free_trans_manager = FreeTransactionManager()
        self.fork_manager = ForkManager()

    def add_transaction(self, transaction: Transaction) -> List[BlockSimple]:
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
        self.free_trans_manager.add_transaction(transaction)

        if self.free_trans_manager.num_free() >= self.trans_per_block:
            # TODO: get the latest transactions for the users
            valid_trans = self.free_trans_manager.get_valid_trans(self.fork_manager.get_longest_latest_trans_no)
            if len(valid_trans) < self.trans_per_block: 
                return []
            return self.add_new_blocks(valid_trans)
        return []

    def add_new_blocks(self, valid_trans: List[Transaction]) -> List[BlockSimple]:
        """
        Create and add new blocks using the valid transactions to the given form.

        Parameters
        ----------
        valid_trans: [Transaction]
            List of transactions to add to the new block(s).
            Assumes that the transactions are ordered by transaction number.

        Returns
        -------
        list(BlockSimple):
            All the blocks added
        """
        log_info(logging, "Adding new blocks to the chain...")
        trans_to_remove = []
        fork = self.fork_manager.get_longest_fork()
        latest_block_hash = fork.head_block_hash if fork else NULL_BLOCK_HASH
        blocks_added = []
        while len(valid_trans) >= self.trans_per_block:
            new_block = create_block(valid_trans[0:self.trans_per_block],
                                     latest_block_hash,
                                     self.difficulty)
            self.block_map.add(new_block)
            latest_block_hash = new_block.block_header.block_hash

            trans_to_remove.extend(valid_trans[0:self.trans_per_block])
            valid_trans = valid_trans[self.trans_per_block:]
            blocks_added.append(new_block)
        self.fork_manager.add_blocks(blocks_added)
        remove_failures = self.free_trans_manager.remove_older_and_equal_trans(trans_to_remove)
        if len(remove_failures) > 0:
            log_critical(logging, "Something went wrong when adding transactions.")
            log_critical(logging, "Failed to remove the following unadded transactions after they were added to a block.")
            for t in remove_failures:
                log_critical(logging, str(t))
        self.cleanup()
        log_info(logging, f"Added: {len(blocks_added)} blocks.")
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
        if incoming_block.hash() in self.block_map:
            raise BlockWasAlreadyAddedError(incoming_block.block_header.block_hash)

        ret_val = self.fork_manager.add_blocks([incoming_block])
        if ret_val[0] != 1:
            log_error(logging, f"Error: {ret_val[0]}")
            return ret_val[0]
        
        self.block_map.add(incoming_block)
        self.free_trans_manager.update_trans_in_inc_block(incoming_block.transactions)
        self.free_trans_manager.remove_older_and_equal_trans(incoming_block.transactions)
        return incoming_block

    def cleanup(self):
        """
        Cleans up the blockchain by removing any fork that has become too
        short compared to the longest fork and moves all its transactions into
        the list of transactions that can be added.
        """
        released_bhashes = self.fork_manager.cleanup_forks(self.block_map)
        for bhash in released_bhashes:
            block = self.block_map[bhash]
            for trans in block.transactions:
                try:
                    self.free_trans_manager.add_transaction(trans)
                except TransWasAlreadyAddedError as e:
                    pass 
                except Exception as e:
                    log_error(logging, str(e))

            self.block_map.remove(bhash)
        
    def to_json(self):
        """
        Returns json version of this BlockChain

        Returns
        -------
        dict:
            json representation of the the block chain.
        """
        return {
            FORK_DATA: self.fork_manager.to_json(),
            TRANS_DATA: self.free_trans_manager.to_json(),
            TRANS_PER_BLOCK: self.trans_per_block,
            DIFFICULTY: self.difficulty,
            BLOCK_MAP: self.block_map.to_json()
        }

    def get_blocks_newer(self, timestamp) -> List[BlockSimple]:
        """
        Returns blocks which are newer than the given timestamp.

        Parameters
        ----------

        timestamp: datetime 
            The lower bound on the datetime

        Returns
        -------

        list of BlockSimple:
            Returns the blocks with timestamp newer than the given timestamp.
        """
        return self.block_map.get_blocks(timestamp)

    def get_blocks_newer_json(self, timestamp) -> dict:
        """
        Returns json of blocks which are newer than the given timestamp.

        Parameters
        ----------

        timestamp: datetime 
            The lower bound on the datetime

        Returns
        -------

        dict:
            The blocks with timestamp newer than the given timestamp in dict/json form.
        """
        return self.block_map.to_json(timestamp)

    def get_trans_not_added_json(self) -> dict:
        """
        Returns transactions which have not been added so far in json format.

        Parameters
        ----------

        timestamp: datetime 
            The lower bound on the datetime

        Returns
        -------

        dict:
            The transactionss with timestamp newer than the given timestamp in dict/json form.

        """
        return self.free_trans_manager.to_json()

    def get_trans_not_added(self) -> List[Transaction]:
        """
        Returns transactions which have not been added so far.

        Returns
        -------

        list of Transaction:
            Returns list of transactions not yet added.
        """
        return self.free_trans_manager.get_trans_list()

    def get_block_list(self) -> List[BlockSimple]:
        """
        Returns all the blocks in list form.

        Returns
        -------

        list of BlockSimple:
            Returns list of blocks in the blockchain.

        """
        return list(self.block_map.values())
