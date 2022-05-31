"""
Contains class related to transactions.
"""
from collections import defaultdict
from datetime import datetime
import numpy as np
from blockchain_proto.puzzle import concat_strs, sha_256_hash_string
from blockchain_proto.consts import *


class Transaction(object):
    """
    Represents a dummy transaction for the proto-blockchain. 
    This is simply a string with the only constraint that the 
    length must be < 64. 

    Parameters
    ----------

    trans_str: str
        A string describing this transaction.
    """
    def __init__(self,  user_id: str, trans_no: int, trans_str: str) -> None:
        assert len(trans_str) <= 64
        self.user_id = user_id
        self.trans_no = trans_no
        self.trans_str = trans_str

    def validate(self) -> bool:
        return len(self.trans_str) <= 64

    def __str__(self):
        return f"{self.user_id} {self.trans_no} {self.trans_str}"

    def __lt__(self, other):
        if not isinstance(other, Transaction):
            return True
        if self.user_id == other.user_id:
            return self.trans_no < other.trans_no
        return self.user_id < other.user_id

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self.user_id == other.user_id and self.trans_no == other.trans_no

    def to_json(self):
        """
        Returns a json representation of of this transaction.

        Returns
        -------
        dict:
            Json version of this transaction.
        """
        return {USER_ID: self.user_id, TRANS_NO: self.trans_no, TRANS_STR: self.trans_str}

    @staticmethod
    def get_trans_hash(trans_list):
        return sha_256_hash_string("".join([str(t) for t in trans_list]))

class TransactionManager:
    """
    Maintains the transactions at this node that has not
    yet been added to any block in any fork.
    """
    def __init__(self):
        self.user_curr_trans = defaultdict(lambda : [])
        self.user_curr_trans_no = defaultdict(lambda : [])
        self.user_max_trans = defaultdict(lambda : 0)

        self.num_trans = 0

    def add_transaction(self, trans: Transaction):
        """
        Adds a transaction to the list of transactions not yet added
        and creates a new block(s) if there are sufficiently many new
        transactions. Raises a ValueError if the transaction was added
        before.

        Parameters
        ----------
        trans: Transaction
            The transaction to add.
        """
        if (trans.user_id in self.user_max_trans and
                trans.trans_no <= self.user_max_trans[trans.user_id]) or \
                trans.user_id in self.user_curr_trans_no:
            raise ValueError(f"Transaction User: {trans.user_id}, no. : {trans.trans_no} was already added.")
        self.user_curr_trans[trans.user_id].append(trans)
        self.user_curr_trans_no[trans.user_id].append(trans.trans_no)
        self.num_trans += 1
        return True

    def __len__(self) -> int:
        return self.num_trans

    def get_valid_trans(self, last_trans_dict: dict) -> [Transaction] :
        """
        Returns the latest set of valid transactions for each user.

        Parameters
        ----------

        last_trans_dict: dict
            The latest transactions for the set of users in some
            fork.

        Return
        ------
        [Transaction]:
            The set of transactions that may be added to the fork without
            violating the constraint that for each user all the transactions
            be in sequence within the fork.
        """
        ret_trans = []
        for user_id in self.user_curr_trans:
            all_trans = self.user_curr_trans[user_id]
            all_trans = sorted(all_trans)
            all_trans_no = np.array([trans.trans_no for trans in all_trans])
            if user_id not in last_trans_dict:
                if all_trans[0].trans_no != 0:
                    continue
                begin = 0
            else:
                begin = all_trans_no[all_trans_no == last_trans_dict[user_id] + 1]
                if len(begin) == 0:
                    continue
                begin = begin[0]

            end = np.where( (all_trans_no[1:] - all_trans_no[0:-1]) > 1 )[0]
            if len(end) == 0:
                ret_trans.extend(all_trans[begin:])
            else:
                ret_trans.extend(all_trans[begin:end[0]])

        return ret_trans

    def remove_older_and_equal_trans(self, sorted_trans_list: [Transaction]) -> None:
        """
        For each user removes from the dictionary of user transactions all the
        transactions that are in the given list, and also all the transactions
        that are older than any of the transactions in the list.

        Parameters
        ----------

        sorted_trans_list: [Transaction]
            The list of transactions to remove. For each user
            all the transactions are assumed to have contiguous trans_no.
        """
        first_trans = {}
        user_trans_no_dict = defaultdict(lambda : [])
        # remove transactions in the list
        for trans in sorted_trans_list:
            try:
                if trans.user_id not in first_trans:
                    first_trans[trans.user_id] = trans.trans_no
                self.user_curr_trans[trans.user_id].remove(trans)
                self.user_curr_trans_no[trans.user_id].remove(trans)
                self.num_trans -= 1
                user_trans_no_dict[trans.user_id].append(trans.trans_no)
            except Exception as e:
                print(e)

        for user_id in user_trans_no_dict:
            self.user_max_trans[user_id] = max(user_trans_no_dict[user_id])

        # remove all older transactions
        for user_id in first_trans:
            old_len = len(self.user_curr_trans[user_id])
            self.user_curr_trans[user_id] = list(filter(lambda t: t.trans_no <= first_trans[user_id],
                                                        self.user_curr_trans[user_id]))
            self.user_curr_trans_no[user_id] = list(filter(lambda t: t <= first_trans[user_id],
                                                           self.user_curr_trans_no[user_id]))
            self.num_trans -= old_len - len(self.user_curr_trans[user_id])

    def to_json(self):
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
