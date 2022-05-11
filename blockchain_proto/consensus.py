"""
Implements the consensus algorithm for a single node.
"""
from blockchain_proto.blockchain_ds import BlockChain

def blockhain_consensus(bc: Blockchain,
                        ext_trans: Queue<str>,
                        node_trans: Queue<str>,
                        new_block: Queue<Block>):
    while True:
        # wait until there are transactions or blocks to process
        while empty(ext_trans) and empty(node_trans) and empty(new_block):
            wait()

        invalid_trans = []
        for trans in concatenate(ext_trans, node_trans):
            if validate_transaction(trans_not_added):
                communicate_transaction_to_peers(trans)
                nb = add_transaction(bc, trans)
                if nb is not null:
                    communicate_new_block_to_peers(nb)

        # check if any new block has been received and process them
        for new_block in new_block_Q:
            new_block = new_block_Q
            if validate_block(blockchain, new_block):
                add_external_block(blockchain, block)
            else:
                communicate_invalid_block(block)