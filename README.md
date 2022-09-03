Copyright 2022 M. M. Hassan Mahmud

# A Technical Introduction To Blockchain

The articles and code in this repo gives a technical introduction to the core ideas of the blockchain technology. The repo is meant to be a resource that a programmer would find useful when learning about this blockchains. The documentation covers only at a *high level* what blockchains are and their purpose, but takes an *in depth* look into how they are implemented under the hood. 

As part of the in depth look, we give pseudo-code describing the main procedures involved in creating and running a blockchain, and also give a executable implementation of a proto-blockchain which can be run on a single or multiple machines. It is a proto-blockchain because it lacks many features like security, scalability etc. necessary for real applications. Indeed, it is purely for pedagogical purposes, but has the basic components that you are likely to see in a full fledged blockchain platform like Ethereum. We chose python (specifically version 3.7.5) as the implementation language partly because of its popularity and simplicity - and partly because I am a researcher/practitioner in AI, where python is the language of choice!


**About the reader:** We will assume the reader a) knows/enjoys programming, b) is familiar with some standard computer science (CS) technologies like public/private key cryptography, peer to peer systems etc. and c) prefers to understand things by building them. If you are not such a reader, there are better resources out there for you. An example is the book [1], which we are using as a starting point and reference for this work. Another recent exhaustive article is [2]. But of course, you are welcome to follow along for as long as it suits you. But please be warned that if something is a standard piece of CS tech, I will use it without further explanation (but will also try to link to a source that we feel is authoritative).

**Why does this exist:** We believe what makes this introduction different from others is that it combines
- a focus on the helping the reader understand the consensus algorithm, which we believe is the core innovation of blockchain, 
- a working implementation of a proto-blockchain concretely illustrating the ideas, 
- and its relative brevity in covering both of the above.

As a point of comparison, the reader may consult [3].

**No Really, why does this exist?** Ok, time to come clean. A big reason this exists is because I was trying to understand blockchains myself, and a great way to learn a new topic is to write up an intro/survey for others and, where relevant, implement the relevant concepts yourself. It has the double benefit of identifying gaps in your knowledge, and providing a service to the community.


## Documentation Guide

The rest of the documentation is divided into the following parts:

- [**Blockchain Quick Introduction**](./docs/bc_proto_quick_intro.md) A quick introduction to the basic ideas of blockchain at a high level. 

- [**Preliminaries**](./docs/bc_proto_prelim.md) Some preliminary topics around hash functions that play an important role in blockchains.

- [**The Blockchain Data Structure**](./docs/bc_proto_blockchain_ds.md) An introduction to the basic components of the blockchain data structure, why they are there.

- [**Merkel Tree**](./docs/bc_proto_merkel_tree.md) A data structure that is often used to store transactions/data within a blockchain, and which provides certain fast validation capabilities.

- [**The Consensus Algorithm**](./docs/bc_proto_consensus_algorithm.md) The distributed consensus algorithm  that ensures that all the nodes within a blockchain have a consistent record of the data.

- [**A Proto-Blockchain Implementation**](./docs/bc_proto_implementation.md) Discusses how to use the proto-blockchain implemented in this repo and hints on its implementation. 

- [**Final Words**](./docs/bc_proto_final_words.md) Some final thoughts on the articles and where to go from here. 


It is recommended you read the above articles in sequence.

## Acknowledgements

I would like to give my sincerest thanks to Nathan Coulson and Andrei Baloiu (both members of this repo) for reading first drafts of the documentation and providing valuable comments which I believe have helped improve the material substantially. Any flaws, inaccuracies, omissions and bugs that remain are my responsibility and mine alone. 


## References

[1] Drescher, Daniel. *Blockchain Basics: A Non-Technical Introduction in 25 Steps*. Apress, 2017, 1st ed. Edition

[2] Clark, Mitchcell. *Blockchain Explained, Blocks? Chains? How does this whole thing work?* The Verge, Sep 9, 2021, 6:00am EDT. https://www.theverge.com/22654785/blockchain-explained-cryptocurrency-what-is-stake-nft

[3] Antonopoulos, Andreas. _Master Bitcoin: Programming the Open Blockchain Paperback._ O'Reilly Publications, 2017.

<hr>

*This software is version 0.1-b.1.*