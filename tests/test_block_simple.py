"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Tests for creating a BlockSimple
"""
from datetime import datetime
from blockchain_proto.blockchain.block_simple import BlockHeader, BlockSimple
from blockchain_proto.transactions.transaction import Transaction
from blockchain_proto.consts import BLOCK_HASH, TRANS_HASH, \
    PREV_BLOCK_HASH, TIMESTAMP, DIFF, NONCE, BLOCK_HEADER, \
    BLOCK_TRANS


def create_block_header():
    return BlockHeader(
        block_hash="block_hash",
        transactions_hash="trans_hashes",
        prev_block_hash="prev_block_hash",
        timestamp=datetime.now(),
        difficulty=3,
        nonce="1")


def create_transactions():
    tr1 = Transaction(user_id="User 1",
                      trans_no=23,
                      trans_details="Pay Bob 23 Gold coins")
    # test ordering
    tr2 = Transaction(user_id="User 1",
                      trans_no=24,
                      trans_details="Pay Bob 23 Gold coins")
    tr3 = Transaction(user_id="User 1",
                      trans_no=23,
                      trans_details="Pay Bob 23 Gold coins")
    tr4 = Transaction(user_id="User 2",
                      trans_no=1,
                      trans_details="Pay Bob 23 Gold coins")

    return tr1, tr2, tr3, tr4


def test_block_header():
    bh = create_block_header()

    # test conversion to json
    bh_json = bh.to_json()
    keys = [BLOCK_HASH,
            TRANS_HASH,
            PREV_BLOCK_HASH,
            TIMESTAMP,
            DIFF,
            NONCE]
    
    for key in keys:
        assert key in bh_json

    assert bh_json[BLOCK_HASH] == bh.block_hash and \
           bh_json[TRANS_HASH] == bh.transactions_hash and \
           bh_json[PREV_BLOCK_HASH] == bh.prev_block_hash and \
           bh_json[TIMESTAMP] == bh.timestamp and \
           bh_json[DIFF] == bh.difficulty and \
           bh_json[NONCE] == bh.nonce


def test_block_simple():
    bh = create_block_header()
    trans_list = list(create_transactions())
    bs = BlockSimple(
        block_header=bh,
        transactions=trans_list
    )

    # test to_json
    bs_json = bs.to_json()

    assert BLOCK_HEADER in bs_json and BLOCK_TRANS in bs_json \
           and len(bs_json) == 2
    bh_json = bh.to_json()
    for key in set(bh_json.keys()).union(bs_json[BLOCK_HEADER].keys()):
        assert bh_json[key] == bs_json[BLOCK_HEADER][key]

    for tr, bs_tr_json in zip(trans_list, bs_json[BLOCK_TRANS]):
        tr_json = tr.to_json()
        for key in set(tr_json.keys()).union(bs_tr_json.keys()):
            assert tr_json[key] == bs_tr_json[key]


if __name__ == '__main__':
    test_block_header()
    test_block_simple()
