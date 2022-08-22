"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Class representing a single transaction.
"""
from blockchain_proto.blockchain.puzzle import sha_256_hash_string
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
    def __init__(self,  user_id: str, trans_no: int, trans_str: str):
        assert len(trans_str) <= 64
        self.user_id = user_id
        self.trans_no = trans_no
        self.trans_str = trans_str

    def validate(self) -> bool:
        return len(self.trans_str) <= 64

    def __str__(self) -> str:
        return f"{self.user_id}: [{self.trans_no}] {self.trans_str}"

    def __lt__(self, other) -> bool:
        if not isinstance(other, Transaction):
            return True
        if self.user_id == other.user_id:
            return self.trans_no < other.trans_no
        return self.user_id < other.user_id

    def __eq__(self, other) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self.user_id == other.user_id and self.trans_no == other.trans_no

    def to_json(self) -> dict:
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


