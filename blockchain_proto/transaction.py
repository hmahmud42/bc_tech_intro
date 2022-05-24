"""
Contains class related to transactions.
"""
from collections import defaultdict
import numpy as np
from blockchain_proto.puzzle import concat_strs, sha_256_hash_string



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

    @staticmethod
    def get_trans_hash(trans_list):
        return sha_256_hash_string(concat_strs([str(t) for t in trans_list]))


class TransactionManager:
    """
    Maintains the transactions at this node that has not
    yet been added to any block in any fork.
    """
    def __init__(self):
        self.user_trans_map = defaultdict(lambda : [])
        self.num_trans = 0

    def add_transaction(self, trans: Transaction)  -> None:
        self.user_trans_map[trans.user_id].append(trans)
        self.num_trans += 1

    def __len__(self) -> int:
        return self.num_trans

    def get_valid_trans(self, last_trans_dict: dict) -> [Transaction] :
        """
        Returns the latest set of valid transactions for each user
        """
        ret_trans = []
        for user_id in self.user_trans_map:
            all_trans = self.user_trans_map[user_id]
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

    def remove_trans(self, trans_list: [Transaction]) -> None:
        for trans in trans_list:
            try:
                self.user_trans_map[trans.user_id].remove(trans)
                self.num_trans -= 1
            except Exception as e:
                print(e)










