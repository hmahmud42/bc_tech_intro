# Part 2: The Blockchain Data Structure

Recall that the term blockchain, in addition to  also refers to a special type of data structur  which is at the core of peer to peer distributed ledger technology.  In this section we describe how this blockchain data structure works. As we will see, it is essentially a very clever way of using public/private key cryptography and hash functions to ensure the integrity of the contents of distributed ledger (i.e. a peer to peer system with no trusted central authority and no way to trust the other peers). The python implementation we build along the way will make the ideas much more concrete. We will begin by looking at blocks.


## Blocks

The blockchain data structure is a chain of blocks, similar to a [linked list](https://en.wikipedia.org/wiki/Linked_list). At a high level, each block contains the following components:

1. a set of transactions in the ledger in the form of a Merkle tree (more on this in the second article) 
2. link to the previous block in the chain
3. information certifying that the block was created in a way that may be trusted.

Figure Blockchain Basic illustrates this idea.

![Figure: Blockchain Basic](figures/blockchain_basic.png)

### Contents of a single simplified block

Since the above is somewhat involved, we will build up our blockchain data structure in two versions. In the first version, we will ignore Merkel trees for storing transactions and instead just use an array. So each block in the first version of our blocks will have the following data: 

1. an array of transactions, each of which is just some text (i.e. a string)

2. a link to the previous block in the chain in the form of a _previous-block-header_ which is a fixed length hexadecimal string (64 bytes in our implementation)

3. the solution to a cryptographic mining puzzle (see below) in the form of a _nonce_ (it's just a name for a 'short string', but the special terminology indicates it has some cryptsographic significance)

4. _timestamp_ of when the block was created

5. a _block-header_  which is also a fixed length hexadecimal string (64 bytes in our implementation)

For reasons that will become clearer later, we will refer to the transactions, the previous-block-header, and the timestamp as the *data* of the block.


### A Simplified Block in `python`

The full code implementing the basic blockchain data structure is available [here](../blockchain_proto/blockchain_ds.py). The following snippets gives the constructor of a python class defining a single basic block. 


The block is constructed by supplying the header of the previous block (or a default string if this is the first block in the chain), a list of transactions (each of which is a string) and a nonce. The code just copies over the data to object attributes and also initializes the timestamp attributed. 

```python
#SNIPPET-1

class BlockBasic(object):
    """
    Class implementing a basic block in the basic blockchain
    data structure implemented below.

    Parameters
    ----------

    prev_block_header: str
        Hash of the previous block in the chain.

    transaction_list: str list
        A list of transactions to add to the block.

    mining_puzzle_solution: str
        Solution to solved puzzle
    """
    def __init__(self, prev_block_header, transaction_list, nonce):
        self.transaction_list = transaction_list
        self.prev_block_header_checked = \
            prev_block_header if prev_block_header is not None \
                else NO_PRECEDING_BLOCKS
        self.nonce = nonce
        self.timestamp = str(datetime.now())
```

The first interesting thing happens when an intermediate header is created by first concatenating the previous-block-header, the (flattened) list of transactions, and the timestamp, and then generating a hash of the resulting string. The hash is calculated by applying the SHA-256 function and is a hexadecimal string of length 64. The idea behind hashing all the contents is to create a _thumbprint_ of signature of the these elements of the block which can be used to check if the transactions in the current block or any of the previous block was changed by someone. We will address this in detail in the next section. 
```python
        intermediate_header = sha256(
            (self.prev_block_header_checked +
             flatten(self.transaction_list) +
             self.timestamp).encode('utf-8')
        ).hexdigest()
```

But for now a function is called to check if the intermediate header concatenated with the nonce forms a valid solution for a cryptographic mining puzzle. For the moment just think of the any puzzle which is computationally very expensive to solve but cheap to verify. You can even think of it as a very large Sudoku puzzle. We will look at this in detail in the next section.

```python
        if not mining_puzzle_verifier(intermediate_header + self.nonce):
            raise InvalidMiningSolutionError("The nonce supplied does not solve the mining puzzle.")
```

If the verification is successful, the block-header attribute of the object is created by applying the SHA256 function on a string. That string is concatenation the intermediate header, the nonce, and all the elements that were used to create intermediate header. As such, this block-header serves both as an id for the block, and as a digital thumbprint of its contents which can be checked to see if the block was modified. Note that the previous-block-header is also an object of the same kind.            
```python
        self.block_header = sha256(
            intermediate_header +
            self.nonce +
            self.prev_block_header_checked +
            flatten(self.transaction_list) +
            self.timestamp).encode('utf-8')
        ).hexdigest()
```


In the next subsection we will see how the hash based structures introduced above helps make a chain of blocks tamper resistant. 

**A note on hashes.** There are several different hashes involved in defining the data for a single block.  To reduce confusion, we list the hashes we have mentioned so far.

1. The _previous-block-header_ which is a hash of the data in the preceding block in the chain, and is a reference to that block and its id.

2. The _intermediate header_, which is a hash created to verify a cryptographic mining puzzle .

3. The _block-header_ which is a hash of the data within the block (including the previous block header) which serves as an id and thumbprint of this block.


## Tamper Resistant Chain of Blocks

In this section we look at how we can chain together a set of blocks so that any tampering with the data in one of the blocks can be detected very quickly. This will turn out to be, in essence, the blockchain datastructure. We will begin by looking at a particular uniqueness property of hash functions.

### Uniqueness of Hash Functions

The blockchain datastructure relies very heavily on the well known "uniqueness property" of hash functions like SHA-256. This property means that given two different strings, say `string-1` and `string-2`, with very high probability, `SHA-256(string-1)` will be different from `SHA-256(string-2)`. You can check this by running the sha256 python function in the snippet above on many different strings.

It is important to understand that it is generally safe to assume that the probability of _collision_ (that is two different strings having the same hash) in practice is `0`. For instance for SHA-256 the collision probability  `1.47*10^(-29)` - roughly the same as flipping a fair coin and getting `~97` heads in a row, a practical impossibility. If for any reason you are not happy with this probability, you can always switch to a hash function with a even smaller collision probability, at the cost of higher computational cost.

The reason the uniqueness property is useful is that for long strings (like some piece of data), the hash acts like a thumbprint or a signature which we can store without needing to store the string itself. If subsequently we are presented with some string which is being claimed as the original string, we can calculate the hash of the new string and compare with the stored hash to validate this claim. This property will come in very handy below.

### Chaining Blocks

In this section we will use hash functions to chain blocks in such a way that any tampering in the contents of a single block invalidates the chain from that block onwards.

To understand the idea, imagine we have created `10` blocks, numbered `0` to `9`, such that `block(i)` refers to the i'th block. Also assume that the blocks are created in such a way that the previous-block-header of `block(i)` is the block-header for `block(i-1)` [add a diagram]. This implies that we must have created the blocks in sequence, `block(i)` after `block(i-1)`, because otherwise we would not be able to use the block-header for `block(i-1)` to create the block-header for `block(i-1)` (this is the third string in the call to `sha256()` in the last snippet). This sequence of `10` blocks , chained in this way, **is a blockchain data structure**. Note that given a set of blocks, it is very easy to verify that the chain is valid.

Creating the blocks in this way also means that if we change any of the data in `block(i)` - in particular the transaction, the timestamp or link to the previous block - the chain will no longer be valid from `block(i)` onwards and will need to be recreated. At the risk of belabouring the obvious, I will show explicitly why this is by reproducing the code for creating the header.
```python
        self.block_header = sha256(
            intermediate_header +
            self.nonce +
            self.prev_block_header_checked +
            flatten(self.transaction_list) +
            self.timestamp).encode('utf-8')
        ).hexdigest()
```
So once `block(i)` is tampered with, by the uniqueness property of hash functions, and block-header calculated using the above code for `block(i)` will be different and will need to be updated. This will also cascade to `block(i+1)` as its previous-block-header (the block-header for `block(i)`), and its block-header will also need to be updated. By the same reasoning all the block headers from then on will need to be updated to keep this a valid blockchain.

You might be thinking, ok great - we tamper one block then we update it and all the subsequent block-headers - so what? The "so what" is where the mining puzzle comes in. Reproducing the code for creating the intermediate header,
```python
        intermediate_header = sha256(
            (self.prev_block_header_checked +
             flatten(self.transaction_list) +
             self.timestamp).encode('utf-8')
        ).hexdigest()
```
note that it is created using the data in the block itself. This is then used to validated the mining puzzle to find the nonce (reproducing code again)
```python
        if not mining_puzzle_verifier(intermediate_header + self.nonce):
            raise InvalidMiningSolutionError("The nonce supplied does not solve the mining puzzle.")
```
which are then finally input to create the block-header. So this means that if we change to the data in block `block(i)`, we will need to solve a new mining puzzle for each of the subsequent blocks. So tampering a transaction will require solving a whole bunch of very computationally expensive puzzles (taking months), and the older the transaction you want to tamper with, the more (prohibitively) expensive this tampering will be.


Now remember that we want to use the blockchain data structure to store a peer to peer distributed ledger. Which means that this data structure will need to be sent from one peer/node to another peer/node. When a node receives a chain of blocks, it will want to be sure that the transactions or timestamp or the ordering of the blocks were not tampered with by the sender. The node can easily verify that the structure is valid. At the same time it will exceedingly (if not prohibively) difficult for the node to tamper with transactions, particularly older ones.

The rest of the code defining a basic blockchain, with the usual infrastructure for adding a block, traversing it etc. is given in [here](../blockchain_proto/blockchain_ds.py). This is straightforward given the above explanation and so I will not get into in depth for that.
