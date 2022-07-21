"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Code for managing forks in the chain.
"""
from datetime import datetime
from typing import List
from blockchain_proto.fork_helper import BlockDepthManager, ForkValidator
from blockchain_proto.block_simple import BlockSimple
from blockchain_proto.consts import *


class Fork:
    """
    Container class for information pertaining to a fork in an
    underlying blockchain

    Parameters
    ----------

    fork_id: int
        The id of the fork.

    block_hash: str
        The hash of the latest block in the fork.

    timestamp: datetime
        Timestamp of when the block was created

    num_blocks: int
        The number of blocks in the fork.

    user_trans_dict: dict
        Dictionary mapping each user_id to the trans_no for the
        latest transaction for that user.

    fork_start_block_hash: str:
        Block hash of the first block in the fork off of the previous trunk
    """
    def __init__(self,
                 fork_id: int,
                 head_block_hash: str,
                 timestamp: datetime,
                 num_blocks:int,
                 fork_start_block_hash: dict):
        self.fork_id  = fork_id
        self.head_block_hash = head_block_hash
        self.timestamp = timestamp
        self.num_blocks = num_blocks
        self.fork_start_block_hash = fork_start_block_hash
        
    def to_json(self) -> dict:
        """
        Returns the json version of this fork.
        
        Returns
        -------
        dict:
            Json of this fork.
        """
        return {        
           FORK_ID: self.fork_id,
           BLOCK_HASH: self.head_block_hash,
           TIMESTAMP: self.timestamp,
           NUM_BLOCKS: self.num_blocks,
           FORK_START_BLOCK_HASH: self.fork_start_block_hash
        }        
        

class ForkManager:
    """
    This class manages the set of forks for the underlying blockchain.
    It is responsible for maintaining the set of forks, the longest
    fork, validating incoming transactions with respect to the fork it
    was added to.
    """
    def __init__(self):
        self.next_fork_id = 0
        self.longest_fork = None
        self.forks = {}
        self.fork_hashes = {}
        self.fork_len_disc = 6
        self.block_depth_manager = BlockDepthManager()
        self.validator = ForkValidator(self)
        
    def get_longest_fork(self) -> Fork:
        """
        Returns the longest fork.

        Return
        ------
        Fork:
            The longest fork.
        """
        return self.longest_fork

    def fork_length(self, fork):
        """
        Returns the length of the given fork

        Parameter
        ---------
        fork: ForkManager
            The fork for which to return the length
        
        Returns
        -------
        int:
            The length of the fork
        """
        return self.block_depth_manager.get_depth(fork.block_hash)

    def _find_insert_fork(self, block):
        """
        Find the fork that block should go into and None
        if no such fork can be found.

        Parameters
        ----------

        block: [BlockSimple]
            The block to find the target fork for.

        Return
        ------

        Fork:
            The fork where block should be insereted.
        """
        return self.fork_hashes[block.prev_hash()] \
            if block.prev_hash() in self.fork_hashes else None

    def _add_new_fork(self, block):
        """
        Changes the head of the block to point to this new block.

        Parameters
        ----------

        block: BlockSimple
            The block to use as the head block for creation.

        Returns
        -------

        Fork:
            The newlys created fork. 
        """
        bhash = block.hash()
        new_fork = Fork(
            fork_id=self.next_fork_id,
            head_block_hash=bhash,
            timestamp=block.block_header.timestamp,
            num_blocks=self.block_depth_manager.get_depth(block.hash()),
            fork_start_block_hash=bhash)

        self.fork_hashes[bhash] = new_fork
        self.forks[new_fork.fork_id] = new_fork
        self.next_fork_id += 1
        return new_fork

    def _change_fork_head(self, fork: Fork, block: BlockSimple):
        """
        Change the head of the given fork to the new block.

        Parameters
        ----------

        fork: Fork
            The fork to change the head for.

        block: BlockSimple
            The block to use as the new head block for the fork.
        """
        del self.fork_hashes[fork.fork_start_block_hash]
        fork.fork_start_block_hash = block.hash()
        fork.num_blocks = self.block_depth_manager.get_depth(block.hash())
        self.fork_hashes[fork.fork_start_block_hash] = fork

    def add_blocks(self, blocks_added: List[BlockSimple]) -> None:
        """
        Adds the given blocks to the appropriate fork, or creates a new
        one if none exists

        Parameters
        ----------

        fork: Fork
            The Fork object to update

        blocks_added: [BlockSimple]
            The list of blocks, in order to add to the fork

        Returns
        -------

        list: 
            For each block, 1 the validation was successful and
            block was added else the error message.
        """
        add_status = []
        for block in blocks_added:
            try:
                self.validator.validate_incoming_block(block)
            except ValueError as v:
                add_status.append(str(v))
                continue
            self.block_depth_manager.add_block(block)
            fork = self._find_insert_fork(block)
            if fork is None: fork = self._add_new_fork(block)
            else: self._change_fork_head(fork, block)
            
            if self.longest_fork is None or fork.num_blocks > self.longest_fork.num_blocks:
                self.longest_fork = fork

            self.validator.add_block(block)
            add_status.append(1)
        
        return add_status


    def get_block_hashes_in_fork(self, fork:Fork, block_map):
        """
        Returns all the hashes for the given fork.

        Parameter
        ---------

        fork: Fork
            The fork for which to return the blocks.

        block_map: dict
            Map from block hashes to blocks.

        Returns
        -------

        list(str):
            The hashes of the blocks in the given fork. 
        """
        ls = []
        cur_block = block_map[fork.block_hash]
        while cur_block.hash() != fork.fork_start_block_hash:
            ls.append(cur_block.hash())
            cur_block = block_map(cur_block.prev_hash())
        ls.append(fork.fork_start_block_hash)
        return ls                

    def cleanup_forks(self, block_map) -> List[str]:
        """
        Drop any fork that is more than 6 blocks shorter than the longest block,
        and release the transactions in the block to be added to the transaction
        manager.
        """
        block_hashes_released = []
        for fork in self.forks.items():
            if fork.num_blocks >= self.longest_fork.num_blocks - 6:
                continue
            bhashes_in_fork = self.get_block_hashes_in_fork(fork, block_map)
            block_hashes_released.extend(bhashes_in_fork)

            for bhash in bhashes_in_fork:
                self.block_depth_manager.remove(bhash)

            del self.forks[fork.fork_id]
            del self.fork_hashes[fork.block_hash]

        return block_hashes_released

    def to_json(self) -> dict:
        """
        Returns a json version of the data in this fork
        manager useful for a user.

        Returns
        -------
        dict:
            Json version of this fork manager useful for a human user.
        """
        return {
            LONGEST_FORK_ID: self.longest_fork.fork_id,
            FORKS: {fork_id: fork.to_json for fork, fork_id in self.forks.items()}
        }
