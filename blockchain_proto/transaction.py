"""
Contains class related to transactions.
"""
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
    def __init__(self, trans_str: str) -> None:
        assert len(trans_str) <= 64
        self.trans_str = trans_str
    
    def validate(self) -> bool:
        return len(self.trans_str) <= 64

    @staticmethod
    def get_trans_hash(trans_list):
        return sha_256_hash_string(concat_strs([t.trans_str for t in trans_list]))
