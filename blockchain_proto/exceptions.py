"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Contains some definitions of some custom exceptions. 
"""

class UnorderedTransactionError(Exception):
    def __init__(self, user_id, bhash):
        message = f"Transactions for {user_id} in block with " +\
           f"hash {bhash} are not in order."            
        super().__init__(message)


class PrecBlockNotFoundError(Exception):
    def __init__(self, bhash, prev_hash):
        message = f"Preceding block {prev_hash[0:10]} for incoming block with hash " +\
           f"{bhash[0:10]}... not found."
        super().__init__(message)


class EarliestTransMismatchError(Exception):
    def __init__(self, user_id, bhash, tran_no, latest_tran_no):
        message = f"Earliest transactions for {user_id} in block with " +\
                  f"hash {bhash} is {tran_no} while latest transaction " +\
                  f"in local chain {latest_tran_no} (should be exactly 1 more)."
        super().__init__(message)


class BlockWasAlreadyAddedError(Exception):
    def __init__(self, bhash):
        message = f"Block with hash {bhash} was already added"
        super().__init__(message)


class TransWasAlreadyAddedError(Exception):
    def __init__(self, user_id, trans_no):
        message = f"Transaction User: {user_id}, no. : {trans_no} was already added."
        super().__init__(message)


class RemoveNonExistentBlockError(Exception):
    def __init__(self, bhash):
        message = f"Trying to remove non-existent block with hash {bhash}."
        super().__init__(message)


# def unordered_trans_msg(user_id, bhash):
#     return f"Transactions for {user_id} in block with " +\
#            f"hash {bhash} are not in order."


# def prec_block_not_found_msg(bhash, prev_hash):
#     return f"Preceding block {prev_hash[0:10]} for incoming block with hash " +\
#            f"{bhash[0:10]}... not found."


# def earliest_trans_mismatch_msg(user_id, bhash, tran_no, latest_tran_no):
#     return f"Earliest transactions for {user_id} in block with " +\
#            f"hash {bhash} is {tran_no} while latest transaction " +\
#            f"in local chain {latest_tran_no} (should be exactly 1 more)."


# def block_was_already_added_msg(bhash):
#     return f"Block with hash {bhash} was already added"


# def remove_non_existent_block_msg(bhash):
#     return f"Tring to remove non-existent block with hash {bhash}."


