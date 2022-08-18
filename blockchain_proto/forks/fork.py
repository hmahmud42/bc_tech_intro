"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Class defining a fork within the blockchain.
"""
from datetime import datetime
from blockchain_proto.consts import FORK_ID, BLOCK_HASH, TIMESTAMP, NUM_BLOCKS, FORK_START_BLOCK_HASH

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
        
