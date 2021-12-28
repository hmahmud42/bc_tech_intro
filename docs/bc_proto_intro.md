# Introduction

The documentation and code in this repo gives a technical introduction to the core ideas of the blockchain. This repo is essentially what I wish were around when I first started learning about this technology. The documendation covers only at a *high level* what blockchains are and their purpose, but takes an *in depth* look into how they are implemented under the hood.

As part of the in depth look, I show how to implement a  proto-blockchain in python from scratch, which can be run on a single or multiple machines. It is a proto-blockchain because it lacks the security and scalability features necessary for real applications. Indeed, it is purely for pedagogical purposes, but has the basic components that you are likely to see in a full fledged blockchain platform like Ethereum. We chose python as the implementation language because of its popularity and simplicity (and partly because I am a researcher/practitioner in AI, where python is all the rage).

 **About the reader:** I will assume the reader a) knows/enjoys programming, b) is familiar with some standard computer science (CS) technologies like public/private key cryptography, peer to peer systems etc. and c) prefers to understand things by building them. If you are not such a reader, there are better resources out there for you. An example is the book [1], which I am using as a starting point and reference for these documentation. Another recent exhaustive article is [2]. But of course, you are welcome to follow along for as long as it suits you. But please be warned that if something is a standard piece of CS tech, I will use it without further explanation (but will also try to link to a source that I feel is authoritative).

The documentation is divided into the following parts:

- [**Part 1: Blockchain Basics**](./bc_proto_blockchain_basics.md) A quick high level introduction to the blockchain technology and its purpose.

- [**Part 2: The Blockchain Data Structure**](./bc_proto_blockchain_ds.md) An introduction to the basic components of the blockchain data structure, why they are there, and an implementation.

- [**Part 3: Merkel Tree**](./bc_proto_merkel_tree.md) A data structure that is often used to store transactions/data within a blockchain, and which provides certain fast validation capabilities.

- [**Part 4: Consesus Algorithm**](./bc_proto_consensus_algo.md) The distributed consensus algorithm  that ensures that all the nodes within a blockchain have a consisitent record of the data.

- [**Part 5: A Running Proto-Blockchain**](./bc_proto_running_blockchain.md) Putting together all the components above to get a running proto-blockchain. Discussion of what its limitations are and where to go from here.

I recommend you read the above in sequence.


## References

[1] Drescher, Daniel. *Blockchain Basics: A Non-Technical Introduction in 25 Steps*. Apress, 2017, 1st ed. Edition

[2] Clark, Mitchcell. *Blockchain Explained, Blocks? Chains? How does this whole thing work?* The Verge, Sep 9, 2021, 6:00am EDT. https://www.theverge.com/22654785/blockchain-explained-cryptocurrency-what-is-stake-nft
