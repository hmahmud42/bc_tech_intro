"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Class representing a single transaction.
"""
from os import stat
from blockchain_proto.blockchain.puzzle import sha_256_hash_string
from blockchain_proto.consts import *


class Transaction(object):
    """
    Represents a dummy transaction for the proto-blockchain. 

    Parameters
    ----------

    user_id: str
        The id of the user conducting this transaction.

    trans_no: int
        The index of this transaction in the list of all the transactions
        carried out by the user.

    trans_details: str
        A string describing this transaction.
    """
    def __init__(self,  user_id: str, trans_no: int, trans_details: str):
        assert len(trans_details) <= 64
        self.user_id = user_id
        self.trans_no = trans_no
        self.trans_details = trans_details

    def validate(self) -> bool:
        return len(self.trans_details) <= 64

    def __str__(self) -> str:
        return f"{self.user_id}: [{self.trans_no}] {self.trans_details}"

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
        return {USER_ID: self.user_id, TRANS_NO: self.trans_no, TRANS_STR: self.trans_details}

    @staticmethod
    def from_dict(trans_dict: dict):
        """
        Creates an instance of a Transaction given a dict version of the transaction.

        Parameters
        ----------

        trans_json: dict
            The transaction represented as a dict.

        Returns
        -------

        Transaction:
            The created transaction
        """
        try: 
            trans_dict['trans_no'] = int(trans_dict['trans_no'])
        except Exception as e:
            return str(e)

        return Transaction(user_id=trans_dict['user_id'], 
                           trans_no=trans_dict['trans_no'],
                           trans_details=trans_dict['trans_details'])

    @staticmethod
    def get_trans_hash(trans_list):
        return sha_256_hash_string("".join([str(t) for t in trans_list]))
