"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Constants used in the project.
"""
node_id_global = {'value': 'Node 1'}

NULL_BLOCK_HASH = "NULL-BLOCK-HASH"
TRANS_GOSSIP = b'transaction'
BLOCK_GOSSIP = b'block'
GET_BLOCKCHAIN = b'get_blockchain'
GET_UNADDED_TRANS = b'get_unadded_trans'
ADD_TRANS = b'add_trans'
NEW_PEER = b'new_peer'
BLOCKS_AND_TRANS = b'blocks_trans'

GET_BLOCKCHAIN_ROUTE = '/get_blockchain'
GET_UNADDED_TRANS_ROUTE = '/get_unadded_trans'
ADD_TRANS_ROUTE = '/add_trans'


USER_ID = 'user_id'
TRANS_NO = 'trans_no'
TRANS_STR = 'trans_str'

TRANS_NOT_YET_ADDED = 'transactions_not_yet_added'

BLOCK_HASH = 'block_hash'
TRANS_HASH = 'transactions_hash'
PREV_BLOCK_HASH = 'prev_block_hash'
TIMESTAMP = 'timestamp'
DIFF = 'difficulty'
NONCE = 'nonce'

FORK_ID =  "fork_id "
NUM_BLOCKS =  "num_blocks"
USER_TRANS_DICT =  "user_trans_dict"
FORK_START_BLOCK_HASH =  "fork_start_block_hash"

LONGEST_FORK_ID = 'longest_fork_id'
FORKS = 'forks'

TRANS_PER_BLOCK = 'trans_per_block'
DIFFICULTY = 'difficulty'
BLOCK_MAP = 'block_map'
TRANS_DATA = 'trans_data'
FORK_DATA = 'fork_data'

BLOCK_HEADER = 'block_header'
BLOCK_TRANS = 'block_trans'

INTERFACE_MSG_TYPE = 'msg_type'
GET_ALL = 'get_all'
GET_BLOCK = 'get_blocks'
GET_TRANS_NOT_ADDED = 'get_trans_not_added'
TIMESTAMP_BOUND = 'timestamp_bound'
