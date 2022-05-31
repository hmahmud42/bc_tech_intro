from datetime import datetime
from blockchain_proto.block_simple import BlockHeader, BlockSimple

from blockchain_proto.consts import BLOCK_HASH, TRANS_HASH, \
    PREV_BLOCK_HASH, TIMESTAMP, DIFF, NONCE


def test_block_header():
    bh = BlockHeader(
        block_hash="block_hash",
        transactions_hash="trans_hashes",
        prev_block_hash="prev_block_hash",
        timestamp=datetime.now(),
        difficulty=3,
        nonce="1")
    
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


if __name__ == '__main__':
    test_block_header()
