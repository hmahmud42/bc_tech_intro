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
- `nonce`: this is the number of transactions from the `from` user that has been added to the blockchain so far + 1. This is to id this transaction specifically, and prevent double transfers (transfering the same item to multiple users). We will discuss this more below.
- `title_name`: a digital id of the object whose ownership is being transferred.

The digital signature for this transaction is created by (roughly speaking) hashing the string corresponding to the transaction and then signing the hash. By the [uniqueness property of hash functions](./bc_proto_blockchain_ds.md#uniqueness-of-hash-functions) and because of the nonce, this is unique for he signed hash can then be verified by using `from`'s public key (which is also their `id` in this instance).



Once created and authorized, they are communicated to the rest of the nodes in the network using a [gossip protocol](https://en.wikipedia.org/wiki/Gossip_protocol). In this protocol, each node peiodically sends all the peers it knows about an updated list of the new transactions that has occured in the node itself and the new transactions it has received, which have not been accepted into a block yet, to all the other nodes it is connected to. Once a node receives a transaction, it assigns it a




## Creating a new block

Once a node has received a sufficiently many new transactions it begins the process of creating a block. To create a block, it creates the Merkel tree for the new transactions, and concatenates the top-hash with the previous-block-header and the timestamp of the current time to create the data for the block. It then solves the mining puzzle to get the nonce [describe various mining puzzles etc.] and then puts them in the block according to the code [here](). That completes creation of the new block. It then adds the new block its own local blockchain and then sends the information to its neighbors via the gossip protocol again.


## Receiving a New Block

When a node receives a new block, it first validates that the transactions are in fact accurate (we already have this code). It then checks to see that the chain structure defined is consistent with what it already has [give examples]. This can happen because its a distributed node and all the nodes are competing to create the blocks. If there are multiple options, then the longest chain is chosen and this information is propagated. Otherwise it stops.


## References

[1] Drescher, Daniel. *Blockchain Basics: A Non-Technical Introduction in 25 Steps*. Apress, 2017, 1st ed. Edition
