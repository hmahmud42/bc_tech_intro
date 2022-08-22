"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Contains some error messages and logging wrapper.
"""
from blockchain_proto.consts import node_id_global


def unordered_trans_msg(user_id, bhash):
    return f"Transactions for {user_id} in block with " +\
           f"hash {bhash} are not in order."


def prec_block_not_found_msg(bhash, prev_hash):
    return f"Preceding block {prev_hash[0:10]} for incoming block with hash " +\
           f"{bhash[0:10]}... not found."


def earliest_trans_mismatch_msg(user_id, bhash, tran_no, latest_tran_no):
    return f"Earliest transactions for {user_id} in block with " +\
           f"hash {bhash} is {tran_no} while latest transaction " +\
           f"in local chain {latest_tran_no} (should be exactly 1 more)."


def block_was_already_added_msg(bhash):
    return f"Block with hash {bhash} was already added"


def remove_non_existent_block_msg(bhash):
    return f"Tring to remove non-existent block with hash {bhash}."


def log_debug(log_obj, msg):
    log_obj.debug(f"[{node_id_global['value']}] " + msg)


def log_info(log_obj, msg):
    log_obj.info(f"[{node_id_global['value']}] " + msg)


def log_warning(log_obj, msg):
    log_obj.warn(f"[{node_id_global['value']}] " + msg)


def log_error(log_obj, msg):
    log_obj.error(f"[{node_id_global['value']}] " + msg)


def log_critical(log_obj, msg):
    log_obj.critical(f"[{node_id_global['value']}] " + msg)
