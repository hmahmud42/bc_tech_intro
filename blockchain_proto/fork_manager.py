"""
Authorization manager for transactions.
"""
from collections import defaultdict
from datetime import datetime
from blockchain_proto.block_creator import validate_block_hashes
from blockchain_proto.block_simple import BlockSimple
from blockchain_proto.transaction import Transaction, TransactionManager

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
                 block_hash: str,
                 timestamp: datetime,
                 num_blocks:int,
                 user_trans_dict:dict,
                 fork_start_block_hash: dict):
        self.fork_id  = fork_id
        self.block_hash = block_hash
        self.timestamp = timestamp
        self.num_blocks = num_blocks
        self.user_trans_dict = user_trans_dict
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
           BLOCK_HASH: self.block_hash,
           TIMESTAMP: self.timestamp,
           NUM_BLOCKS: self.num_blocks,
           USER_TRANS_DICT: self.user_trans_dict,
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
        self.last_fork_id = 1
        self.longest_fork = None
        self.forks = {}
        self.fork_hashes = {}
        self.fork_len_disc = 6
        self.block_depth_map = {}

    def longest_fork(self) -> Fork:
        """
        Returns the longest fork.

        Return
        ------
        Fork:
            The longest fork.
        """
        return self.longest_fork

    def update_block_depths(self, blocks_added: [BlockSimple]):
        """
        Updates the depth of the blocks based on their previous blocks.

        blocks_added: [BlockSimple]
            The list of blocks, in order, to update depths for.
        """
        for block in blocks_added:
            if block.block_header.prev_block_hash != NULL_BLOCK_HASH:
                self.block_depth_map[block.block_header.block_hash] = \
                    self.block_depth_map[block.block_header.prev_block_hash] + 1
            else:
                self.block_depth_map[block.block_header.block_hash] = 1

    def update(self, fork: Fork, blocks_added: [BlockSimple]) -> None:
        """
        Updates the given fork by adding the blocks to it.

        Parameters
        ----------

        fork: Fork
            The Fork object to update

        blocks_added: [BlockSimple]
            The list of blocks, in order to add to the fork
        """
        if fork and fork.fork_id not in self.forks:
            raise ValueError(f"For fork with id {fork.fork_id} and "
                             f"blockhash {fork.block_hash} "
                             f"requested to be updated"
                             f"but fork not in dictionary.")
        self.update_block_depths(blocks_added)

        if not fork:
            self.last_fork_id += 1
            fork = Fork(fork_id=self.last_fork_id,
                        block_hash=blocks_added[-1].block_header.block_hash,
                        timestamp=blocks_added[-1].block_header.timestamp,
                        num_blocks=self.block_depth_map[blocks_added[0].block_header.block_hash] + len(blocks_added),
                        user_trans_dict=defaultdict(lambda : 0),
                        fork_start_block_hash=blocks_added[0].block_header.block_hash)
            self.forks[fork.fork_id] = fork
            prev_hash = None
        else:
            prev_hash = fork.block_hash
            fork.block_hash = blocks_added[-1].block_header.block_hash
            fork.timestamp = blocks_added[-1].block_header.timestamp
            fork.num_blocks += len(blocks_added)

        # assumes transactions within a block are ordered
        # by trans_no for each user_id
        for block in blocks_added:
            for trans in block.transactions:
                fork.user_trans_dict[trans.user_id] = trans.trans_no

        self.fork_hashes[fork.block_hash] = fork
        if prev_hash: del self.fork_hashes[prev_hash]

    def validate_incoming_block(self, inc_block: BlockSimple) -> Fork:
        """
        Validates a block that was received from a peer.
        First makes sure that its previous block hash is in fact there.
        Then ensures that the transactions in the block are in order.
        Then ensures that the puzzle was solved correctly.

        Parameters
        ----------

        inc_block: BlockSimple
            The block to validated.

        Return
        ------

        Fork:
            The fork the block should be added to.
        TODO: deal with out of order blocks.
        """
        prev_block_hash = inc_block.block_header.prev_block_hash
        if prev_block_hash != NULL_BLOCK_HASH and prev_block_hash not in self.fork_hashes:
            raise ValueError(f"Preceding blocks for incoming block with hash "
                             f"{inc_block.block_header.block_hash} not found.")

        user_trans = defaultdict(lambda : [])
        for trans in inc_block.transactions:
            user_trans[trans.user_id].append(trans.trans_no)

        self._validate_block_transaction_order(inc_block, user_trans)

        fork = None
        if prev_block_hash != NULL_BLOCK_HASH:
            fork = self.fork_hashes[prev_block_hash]
            self._validate_block_user_latest_trans(fork, inc_block, user_trans)

        validate_block_hashes(inc_block)
        return fork

    @staticmethod
    def _validate_block_transaction_order(block: BlockSimple, user_trans: dict):
        """
        Validates the transaction order for each user in a given block using the
        user transactions from the block. Raises a value error if validation fails.

        Parameters
        ----------

        block: BlockSimple
            The block for which to validate transaction orders

        user_trans: dict
            Dictionary of mapping each user to the set of transactions.
        """
        for user_id in user_trans:
            tns = user_trans[user_id]
            if not all([tns[i] + 1 == tns[i + 1] for i in range(len(tns) - 1)]):
                raise ValueError(f"Transactions for {user_id} in block with " +
                                 f"hash {block.block_header.block_hash}" +
                                 f"are not in order.")

    @staticmethod
    def _validate_block_user_latest_trans(fork: Fork, block: BlockSimple, user_trans: dict):
        """
        Validates that for each user the oldest transaction in the fork is
        numbered one minus the oldest transaction number for that user
        in the block.

        Parameters
        ----------

        block: BlockSimple
            The block for which to validate transaction orders

        user_trans: dict
            Dictionary of mapping each user to the set of transactions.
        """
        for user_id in user_trans:
            tns = user_trans[user_id]
            if (user_id not in fork.user_trans_dict and tns[0] > 0) or \
                    fork.user_trans_dict[user_id] + 1 != tns[0]:
                raise ValueError(f"Earliest transactions for {user_id} in block with " +
                                 f"hash {block.block_header.block_hash}" +
                                 f"is {tns[0]} while latest transaction in local chain " +
                                 f"is  {fork.user_trans_dict[user_id]}.")

    def cleanup_forks(self, block_map) -> [str]:
        """
        Drop any fork that is more than 6 blocks shorter than the longest block,
        and release the transactions in the block to be added to the transaction
        manager.
        """
        block_hashes_released = []
        for fork in self.forks.items():
            if fork.num_blocks >= self.longest_fork.num_blocks - 6:
                continue

            cur_block = block_map[fork.block_hash]
            block_hashes_released.append(fork.block_hash)
            del self.block_depth_map[cur_block.block_header.block_hash]
            while cur_block.block_header.block_hash != fork.fork_start_block_hash:
                cur_block = block_map(cur_block.block_header.prev_block_hash)
                block_hashes_released.append(cur_block.block_header.block_hash)
                del self.block_depth_map[cur_block.block_header.block_hash]

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
