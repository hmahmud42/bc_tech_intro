# The Blockchain Consensus Algorithm

One of the properties that make blockchain so attractive is that any node/peer within the chain can create a transaction at any point in time and add it to the ledger. But because there is no central authority coordinating the work of the peers, the problem now is how to ensures that all the peers have a consistent view of the ledger - that is they all agree on what transactions are in the ledger and what order the transactions were performed in. This is called the *blockchain consensus problem* and one of the main innovations of the blockchain technology is an algorithm or protocol that helps solve this.

Indeed, the [consensus problem](https://en.wikipedia.org/wiki/Consensus_(computer_science) is a general problem that shows up in all distributed systems and is considered to be very difficult to solve. Many different solutions have been proposed in the past and these have complementary strengths, and are applicable for different use cases. Which is another way of saying that no general solution to the consensus problem exists. The blockchain consensus algorithm in particular solves this problem for distributed ledgers by answering the following questions for each node:

1. How to communicate transactions have been performed at the node and receive transactions that have been performed at the other nodes.

2. How to create a new block using the new transactions and communicate that to other nodes.

3. What to do when other nodes sends  block to be added

4. When and which blocks to add to the local structure and in what order.

We address each of the above issues in turn from the perspective of a single node, and desicribe what it means in terms of the overall state of the distributed ledger. We begin by introducing some main high level ideas that make it all hang together.

## Incentivizing Accuracy and Honesty

One of the key ideas in the blockchain algorithm is that of rewarding nodes that help in maintaining a correct and consistent view of the blockchain. A reward scheme is necessary because there is no central authority to force/ensure that the nodes are not misbehaving (we will see how in subsequent sections).

This reward typically takes the form of fees paid by the nodes that want a transaction stored in the blockchain but can take other forms as well. The fees themselves may be paid using a *token* native to or unique to the blockchain platform, which can in turn be obtained by buying said token in some kind of exchange. However, there are often other forms of reward schemes as well - for instance in the bitcoin protocol, the blockchain that that started it all, the reward is in the form a [certain units of the bitcoin crypotocurrency](https://en.wikipedia.org/wiki/Bitcoin_network#Mined_bitcoins).

The exact form of the reward is not important - what is important is that there *is* a reward in helping maintain the blockchain structure and the reward *is* sufficient to incentivize the nodes in spending the effort required to maintain it. For instance, for bitcoin, the initial incentive for maintaining the network and earning coins was the anticiaption that bitcoins will increase in value in the future (which has certainly [borne out](https://coinmarketcap.com/currencies/bitcoin/) as of writing this document). **However this last example should not, in any shape or form, be considered to be an endorsement of investing in any crypotcurrency.**


## Blockchain Consesus Algorithm Main Loop

Now that we know about rewards, we can define the main loop of the consenus algorithm that runs in a single node and justify why it works. In the main loop, the algorithm is in one of the two following phases:

**A.** Trying to create and add the next block in the chain in competition with the other nodes in the chain.

**B.** Validating and adding to the blockchain a new block that has been created and submitted by a peer.

Both of the phases are motivated by the reward scheme that was mentioned in the previous section. Phase A is motivated by the fact that if a node manages to create the next valid block before everybody else, it will receive the associated reward. Phase B is motivated by fact that if a node can prove that the submitted block is not valid, it can continue working on getting the reward for the current block. Or alternatively if the block is valid, it can get a headstart on starting phase A for the current block.

Phase A for each node consists of the following steps:

1. Receive and validate transactions from connected peers or create transactions at the current node as per the user request.

2. Once sufficient number of transactions have been received, create a new a block using the transactions and send the new block to peers.

Phase B for each node consists of the following steps:

1. Upon receiving a new block ensure that it is a valid block using the logic described in [Part 2: The Blockchain Data Structure](./bc_proto_blockchain_ds.md).

2. If the requested block is valid, then add it to the local blockchain structure (taking care of any forks - see below) and inform the connected peers about the addition of this new block.

So the overall algorithm be described as follows (in a python like pseudocode)

```python
TRANS_PER_BLOCK = 8

def blockhain_consensus(blockchain,
                        ext_trans_Q,
                        node_trans_Q,
                        new_block_Q):
    valid_trans = [] # list of valid transactions not yet added
    invalid_trans = [] # list of invalid transactions

    while True:
        # wait until there are transactions or blocks to process
        while ext_trans_Q.is_empty() and node_trans_Q.is_empty() and
            new_block_Q.is_empty() and len(valid_trans) < TRANS_PER_BLOCK:
            wait()

        # add any new  transactions from peers        
        trans_not_added = ext_trans_Q.as_list() + node_trans_Q.as_list()

        # validate transactions and
        _valid_trans, _invalid_trans = validate_transaction(trans_not_added)
        valid_trans.extend(_valid_trans)
        invalid_trans.extend(_invalid_trans)

        # create a new block if sufficiently new transactions are present
        if len(valid_trans) >= TRANS_PER_BLOCK:
            # The new block possibly contains information about the reward
            # the node receives for creating the new block
            new_block = create_new_block(valid_trans, TRANS_PER_BLOCK)
            add_block(blockchain, new_block)
            communicate_new_block_to_peers(new_block)

        if len(invalid_trans) > 0:
            communicate_invalid_trans_to_peers(invalid_trans)

        # check if any new block has been received and process them
        for new_block in new_block_Q:
            new_block = new_block_Q
            if validate_block(blockchain, new_block):
                add_block(blockchain, block)
            else:
                communicate_invalid_block(block)
```
The algorithm runs in an infinite loop and receives four references as arguments: to the blockchain (`blockchain`), to a queue of transactions from other peers (`ext_trans_Q`), a queue of transactions performed at the current node (`node_trans_Q`) and a queue of new blocks received from peers (`new_block_Q`). All the queues get filled by separate processeses running in parallel. As a first step, the algorithm waits until there are transactions or blocks to process. If there are new transactions, these are added to the list of transactions not yet added to a block. The list of transactions not yet added are then processed to get a list of valid and invalid transactions. If the number of valid transactions are sufficient to create a new block then a new block is created and communicated to the peers. After that any new received from the peers is added to the current blockchain.



## Creating and Communicating Transactions

As we mentioned above, transactions can be created by any node in the blockchain. However any transaction created by the system must be valid in a certain sense. First, it has to pass the proper authorization requirements in the ledger, and second it has to be valid in terms of the other transactions in the blockchain. We discuss each issue in turn.

### Authorizing a Transaction

When a distributed ledger is used to record transfer of some ownership of some item (land, jewellery, guitar, take your pick) between users, it is often protected using [public-key cryptography](https://en.wikipedia.org/wiki/Public-key_cryptography) so that the transfer from user A to any other user is [digitally signed](https://en.wikipedia.org/wiki/Digital_signature) by A's _private key_.
> Since both public-key cryptography and digital signature are well known computer science concepts I will not discuss them in detail beyond the links.

For example a transaction may look like the following
```
{
  from: "0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8",
  to: "0xac03bb73b6a9e108530aff4df5077c2b3d481e5a",
  fee: "2",
  nonce: "43",
  title_name: "ad3843b887aabdcb49f36f9ef6bb1300c5bd4722"
}
```
The above was directly inspired by the transaction form at in Ethereum, which is documented [here](https://ethereum.org/en/developers/docs/transactions/) for what transactions look like in Ethereum. In our example the fields have the following meaning:  
- `from`: the current owner,  digitally identified by their [public key](https://en.wikipedia.org/wiki/Public-key_cryptography)
- `to`: the new owner, also identified by their public key
- `fee`: the fee to be received by the node that successfully creates the block for this transaction (see below).
- `nonce`: this is the number of transactions from the `from` user that has been added to the blockchain so far + 1. This is to id this transaction specifically, and prevent double transfers (transfering the same item to multiple users). Note that this is another `nonce`, different from the one we discussed [before](./bc_proto_blockchain_ds.md#contents-of-a-single-simplified-block). We will discuss this more below.
- `title_name`: a digital id of the object whose ownership is being transferred.

The digital signature for this transaction is created by the `from` user node by (roughly speaking) hashing the string corresponding to the transaction and then digitally signing the hash using `from`'s private key . The signature can then be verified by using the `from` user's public key (which is also their id). This way we can be sure that transaction was authorized by the `from` user.

### Validating A Transaction

Depending on the nature of the items in the blockchain, several different kinds of validation may need to be performed. In the example above we need to ensure that the `from` user actually owns the item in question by looking at the history of the blockchain and noting that an accepted block records `from` user gaining ownership of the item (there may need to be special 'verified ownership' type transactions to intialize the chain with a user owning a particular item - but we don't address those complications here).

We also need to ensure that the same transaction is not written into the blockchain more than once (in the same or different block). This can be done only accepting transaction into a block if another transaction with nonce exactly one less has already been accepted into the blockchain - which ensures the correct sequencing of the transactions for each user.  

### Communicating Transactions

When a node creates a transaction it ensures that it has been properly authorised and it is valid. It performs the same operation when it receives a transaction from another node. In both cases once a transaction has been properly authorized and validated, it is communicated to the rest of the blockchain using the [gossip protocol](https://en.wikipedia.org/wiki/Gossip_protocol). In this protocol, each node peiodically sends all the peers it knows about an updated list of the new transactions that has occured in the node itself and the new transactions it has received, which have not been accepted into a block yet. That's all there is to it.

Of course, each node also needs to perform the necessary functions to ensure that it remains connected to the peer to peer network of the blockchain - this includes
- connecting to the peer to peer network itself by querying one or more trusted servers to identify peers that the node can connect with
- pinging peers to determine if an existing connection is still valid
- retrieving list of additional peers from current peers that the node can connect to.

The number of connections has to trade off between being reliably connected to the peer to peer network for using it and ensuring its proper functioning vs. flooding the network with too much traffic. However, these are standard issues in peer to peer network design and not specific to blockchains - and so I won't discuss them further here.


## Creating and adding a new block

Once a node has received a sufficiently many new transactions it begins the process of creating a block. We went through the detail of how this is done in part [Blockchain Datastructure](./bc_proto_blockchain_ds#a-simplified-block-in-python). However there is one difference in the context of a proper blockchain - instead of hashing the list of transactions as described there, the node creates a [Merkel tree](./bc_proto_merkel_tree.md) for the new transactions and uses the top-hash instead. Once created It then adds the new block its own local blockchain as described in the section [Blockchain Datastructure](./bc_proto_blockchain_ds#a-simplified-block-in-python) and then sends the block to the peers the node is connected to via the gossip protocol again. The code for this can be found [here](todo).


## Receiving a new block

The distributed nature of the blockchain makes processing the receipt of a new block a potentially tricky affair. The problem arises from the fact that it is possible (and it does happen in practice) that different parts of the network, developing independently, may have developed different views of the order in which blocks were added and so the blockchain structure at the local node is different from the one declared in the received block. When this happens, its called *forking* of the blockchain and this needs to dealt with. We first discuss how forking happens and then strategies for dealing with.

### Forking of a blockchain

Let us give an example of how forking may happen. Let us start with a case where the blockchain is at a consistent state `S` - that is all nodes agree on the order of blocks in the ledger. Nodes in real peer to peer networks tend to be clustered into groups, so that nodes within a group have fewer hops between each other. The following figure, taken from [2], shows this effect in an early version of the bitcoin network, where you can clearly see at least four different clusters.

![Bitcoin Network Topology](./figures/bitcoin_topology.png)

So what may happen is nodes within a cluster, say cluster `A`,  may create enough new transactions to constitute a new block. Furthermore, because of the use of the gossip protocol these may be communicated to  a single node `N` in cluster `A` before the same can happen at any other node outside the `A`. `N` may then create a new block with block header (shortened) `ab5ef` and communicate that to the blockchain. By a similar process some other node `M` may also end creating a new block with block header (shortened) `fe121` with possibly a different set of transactions and also communicate that to the rest of the blockchain. Hence because of this some peers will think the blockchain is `S` followed by `ab5ef` and others  will think the chain is `S` followed by `fe121` and a node will only know this when it receives both new blocks at some point. Hence The blockchain has _forked_. The figure below illustrates this.

![Forking Example](./figures/forking_example.png)


### Strategies for dealing with forking


 different nodes may have different views of the blockchain and so the blockchain structure in the new block may contradict the blockchain

The processing that the consensus algorithm performs once it receives a new block reveals an additional complication in maintaining a blockchain which we have not addressed so far.

When a node receives a new block, it first authorizes and validates the  the same way that we described above. It then checks to see that the chain structure defined is consistent with what it already has. This can happen because its a distributed node and all the nodes are competing to create the blocks. If there are multiple options, then the longest chain is chosen and this information is propagated. Otherwise it stops.


## References

[1] Drescher, Daniel. *Blockchain Basics: A Non-Technical Introduction in 25 Steps*. Apress, 2017, 1st ed. Edition

[2] Lischke, Matthias and Fabian, Benjamin. Analyzing the Bitcoin Network: The First Four Years. _Future Network_, 2016, Volume 8, Issue 7.
