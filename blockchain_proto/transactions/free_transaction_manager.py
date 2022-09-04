"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Class for managing 'free' transactions (transactions not belonging to a block)
in a blockchain.
"""
from typing import List, Tuple
from collections import defaultdict
import numpy as np
from collections import defaultdict
from blockchain_proto.transactions.transaction import Transaction
from blockchain_proto.forks.fork_manager import ForkManager
from blockchain_proto.consts import TRANS_NOT_YET_ADDED
from blockchain_proto.exceptions import TransWasAlreadyAddedError

class FreeTransactionManager:
    """
    Maintains the transactions at this node that has not
    yet been added to any block in any fork - i.e. transactions
    that are free.
    """
    def __init__(self):
        self.user_curr_trans = defaultdict(lambda : [])
        self.user_curr_trans_no = defaultdict(lambda : [])
        self.user_max_trans = defaultdict(lambda : -1)
        self.size = 0

    def trans_was_added(self, trans:Transaction) -> bool:
        return  \
            (trans.user_id in self.user_max_trans and
             trans.trans_no <= self.user_max_trans[trans.user_id]) or \
            (trans.user_id in self.user_curr_trans_no and
             trans.trans_no in self.user_curr_trans_no[trans.user_id])

    def num_free(self) -> int:
        """
        Returns the number of free transactions being maintained by this 
        manager.

        Returns
        -------

        int:
            Number of free transactions.
        """
        return self.size

    def add_transaction(self, trans: Transaction) -> bool:
        """
        Adds a transaction to the list of transactions not yet added
        Raises a ValueError if the transaction was added before.

        Parameters
        ----------
        trans: Transaction
            The transaction to add.
        """
        if self.trans_was_added(trans):
            raise TransWasAlreadyAddedError(trans.user_id, trans.trans_no)

        self.user_curr_trans[trans.user_id].append(trans)
        self.user_curr_trans_no[trans.user_id].append(trans.trans_no)
        self.size += 1
        return True

    def __len__(self) -> int:
        return self.size

    def get_valid_trans(self, get_latest_trans) -> List[Transaction] :
        """
        Returns the latest sequence of valid transactions for each user.
        A transaction sequence is valid if: the latest transaction in
        last_trans_dict has trans_no 1 less than the earliest transaction
        in the sequence, and the transaction numbers in the sequence
        are also in sequence - i.e. n, n+1, n+2 etc.

        Parameters
        ----------

        get_last_trans: func
            Function that gets the latest transactions for the set of users in some
            fork.

        Return
        ------
        list of Transaction:
            The sequence of valid transactions that may be added to the fork without
            violating the constraint that for each user all the transactions
            be in sequence within the fork.
        """
        ret_trans = []
        for user_id in self.user_curr_trans:
            all_trans = sorted(self.user_curr_trans[user_id])
            all_trans_no = np.array([trans.trans_no for trans in all_trans])
            # user not in fork the transaction is to be added to.
            latest_trans_no = get_latest_trans(user_id)
            if latest_trans_no == -1:
                if all_trans[0].trans_no != 0:
                    continue
                first_trans_no = 0
            else:
                first_trans_no = np.where(all_trans_no == latest_trans_no + 1)[0]
                if len(first_trans_no) == 0:
                    continue
                first_trans_no = first_trans_no[0]
            latest_trans_no = np.where( (all_trans_no[1:] - all_trans_no[0:-1]) > 1)[0]
            if len(latest_trans_no) == 0:
                ret_trans.extend(all_trans[first_trans_no:])
            else:
                ret_trans.extend(all_trans[first_trans_no:latest_trans_no[0]+1])

        return ret_trans

    def remove_older_and_equal_trans(self, sorted_trans_list: List[Transaction]) -> List[Transaction]:
        """
        For each user removes from the dictionary of user transactions all the
        transactions that are in the given list, and also all the transactions
        that are older than any of the transactions in the list.

        Parameters
        ----------

        sorted_trans_list: [Transaction]
            The list of transactions to remove. For each user
            all the transactions are assumed to have contiguous trans_no.

        Return
        ------

        list of Transaction:
            List of transactions for which the removal failed.
        """
        first_trans, remove_failures = self._remove_trans_in_list(sorted_trans_list)
        self._remove_older_transactions(first_trans)
        return remove_failures

    def _remove_trans_in_list(self, sorted_trans_list: List[Transaction]) -> Tuple[dict, list]:
        """
        For each user removes all the transactions that are in the
        given list from the dictionary of user transactions.

        Parameters
        ----------

        sorted_trans_list: [Transaction]
            The list of transactions to remove. For each user
            all the transactions are assumed to have contiguous.
            trans_no.
        
        Returns
        -------

        dict, list:
            Dictionary of all first transactions in the list for each
            user, and removals which failed.
        """
        first_trans = {}
        user_trans_no_dict = defaultdict(lambda : [])
        remove_failures = []
        # remove transactions in the list
        for trans in sorted_trans_list:
            try:
                if trans.user_id not in first_trans:
                    first_trans[trans.user_id] = trans.trans_no
                self.user_curr_trans[trans.user_id].remove(trans)
                self.user_curr_trans_no[trans.user_id].remove(trans.trans_no)
                self.size -= 1
                user_trans_no_dict[trans.user_id].append(trans.trans_no)
            except Exception as e:
                remove_failures.append(trans)

        for user_id in user_trans_no_dict:
            self.user_max_trans[user_id] = min(user_trans_no_dict[user_id])
        return first_trans, remove_failures
    
    def _remove_older_transactions(self, trans_dict: dict) -> dict:
        """
        For each user in trans_dict, removes all the transactions
        that are older than the transaction in trans_dict. 

        Parameters
        ----------

        trans_dict: dict
            Maps user_id's to transaction numbers        
        """
        # remove all older transactions
        for user_id in trans_dict:
            old_len = len(self.user_curr_trans[user_id])
            self.user_curr_trans[user_id] = list(
                filter(lambda t: t.trans_no <= trans_dict[user_id],
                       self.user_curr_trans[user_id])
            )
            self.user_curr_trans_no[user_id] = list(
                filter(lambda t: t <= trans_dict[user_id], 
                       self.user_curr_trans_no[user_id])
            )
            self.size -= old_len - len(self.user_curr_trans[user_id])

    def update_trans_in_inc_block(self, trans_list: List[Transaction]):
        """
        Updates the internal data structure to account for the transactions in
        trans_list.

        Paramters
        ---------

        trans_list: list of Transaction
            transaction list to update the internal data structures with.
        """
        for trans in trans_list:
            if trans.trans_no > self.user_max_trans[trans.user_id]:
                self.user_max_trans[trans.user_id] = trans.trans_no

    def get_trans_list(self) -> List[Transaction]:
        """
        Returns a json representation of of the data in the transaction manager.

        Returns
        -------
        list of trans:
            Returns the list of the transactions
        """
        return [trans for user_id in self.user_curr_trans for trans in self.user_curr_trans[user_id]]

    def to_json(self) -> dict:
        """
        Returns a json representation of of the data in the transaction manager.

        Returns
        -------
        dict:
            Json version of this transaction.
        """
        return {TRANS_NOT_YET_ADDED:
                    {
                        user_id:  [trans.to_json() for trans in self.user_curr_trans[user_id]]
                        for user_id in self.user_curr_trans
                     }
                }
