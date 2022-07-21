"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Implements helper classes for the fork manager.
"""
from collections import defaultdict, OrderedDict
from typing import List
from blockchain_proto.block_simple import BlockSimple
from blockchain_proto.block_creator import validate_block_hashes
from blockchain_proto.consts import NULL_BLOCK_HASH
from blockchain_proto.messages import unordered_trans_msg, prec_block_not_found_msg, \
    earliest_trans_mismatch_msg, block_was_already_added_msg


class BlockDepthManager:
    """
    Manages block depths
    """

    def __init__(self):
        self.block_depth_map = {}

    def add_block(self, block: BlockSimple):
        """
        Updates the depth of the blocks based on their previous blocks.

        blocks_added: [BlockSimple]
            The list of blocks, in order, to update depths for.
        """
        if block.prev_hash() != NULL_BLOCK_HASH:
            self.block_depth_map[block.hash()] = \
                self.block_depth_map[block.prev_hash()] + 1
        else:
            self.block_depth_map[block.hash()] = 1

    def remove(self, block: BlockSimple):
        """
        Removes the given block from the depth manager.
        """
        del self.block_depth_map[block.hash()]

    def get_depth(self, bhash: str):
        """
        Get the depth of the given block in blockchain.
        """
        return self.block_depth_map[bhash]


class LatestTrans:
    """
    Class that maintains the latest transaction for each user
    in the blocks in a blockchain
    """
    def __init__(self):
        # map blocks to latest transaction per user
        self.trans_map = OrderedDict()
        self.prev_hashes = OrderedDict()

    def add_block(self, block: BlockSimple):
        """
        Updates the trans_map to store the latest transactions
        for each user. Assumes transactions in the block are ordered
        for each user.

        Parameter
        ---------
        block: BlockSimple
            The block for which to update the transactions per user.        
        """
        self.trans_map[block.hash()] = {
            trans.user_id: trans.trans_no for trans in block.transactions
        }
        self.prev_hashes[block.hash()] = block.prev_hash()

    def get_latest_trans(self, user_id: str, start_hash: str):
        """
        Returns the latest transaction for each user in the blockchain
        starting at the given block.

        Parameter
        ---------

        user_id: str
            The user for which to search the latest transaction,

        start_block: BlockSimple
            The block where to start the search.

        Returns
        -------

        int:
            If a transaction for this user is found then the no.
            of that transaction, otherwise -1.
        """
        cur_hash = start_hash
        while True:
            if cur_hash not in self.trans_map:
                return -1 
            if user_id in self.trans_map[cur_hash]:
                return self.trans_map[cur_hash][user_id]
            if self.prev_hashes[cur_hash] == NULL_BLOCK_HASH:
                return -1
            cur_hash = self.prev_hashes[cur_hash]

    def __contains__(self, bhash):
        return bhash in self.trans_map



class ForkValidator:
    """
    Functions for validating blocks that are requested to be added
    to a ForkManager.
    """
    def __init__(self, fork_manager):
        self.fork_manager = fork_manager
        self.latest_trans = LatestTrans()

    def validate_incoming_block(self, inc_block: BlockSimple) -> 'Fork':
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
        prev_hash = inc_block.prev_hash() 
        if prev_hash != NULL_BLOCK_HASH and prev_hash not in self.latest_trans:
            raise ValueError(prec_block_not_found_msg(inc_block.hash(), prev_hash))

        if inc_block.hash() in self.latest_trans:
            raise ValueError(block_was_already_added_msg(inc_block.hash()))

        self.validate_transactions(inc_block)
        validate_block_hashes(inc_block)

    def validate_transactions(self, block):
        """
        Ensures that the transactions in the block are in order for 
        each user, and that the earliest transaction no for each user
        is 1 + the latest transaction already recorded by the validator.
        """
        user_trans = defaultdict(lambda : [])
        for trans in block.transactions:
            user_trans[trans.user_id].append(trans.trans_no)

        self.validate_block_transaction_order(block, user_trans)
        self.validate_user_latest_trans(user_trans, block)

    def validate_block_transaction_order(self, block: BlockSimple, user_trans: dict):
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
                raise ValueError(unordered_trans_msg(user_id, block.hash()))#

    def validate_user_latest_trans(self, user_trans: dict, start_block: BlockSimple):
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
            # TODO: get all the user latest transactions at the same time
            latest_trans = self.latest_trans.get_latest_trans(user_id, start_block.prev_hash()) 
            if latest_trans != user_trans[user_id][0] - 1:
                # Debug messages
                # print(start_block.prev_hash())
                # for item in self.latest_trans.trans_map.items():
                #     print(item)
                # print("\n\n")
                # for item in self.latest_trans.prev_hashes.items():
                #     print(item)

                raise ValueError(earliest_trans_mismatch_msg(
                    user_id, start_block.hash(), user_trans[user_id][0], latest_trans))


    def add_block(self, block):
        """
        Adds the given block as one that incoming blocks should be 
        validated against.

        Parameters
        ----------

        block: BlockSimple
            The block to add
        """
        assert block.hash() not in self.latest_trans
        self.latest_trans.add_block(block)
