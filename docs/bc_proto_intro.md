# Introduction

The articles and code in this repo gives a technical introduction to the core ideas of the blockchain technology. This repo is essentially what I wish were around when I first started learning about this blockchains. The documentation covers only at a *high level* what blockchains are and their purpose, but takes an *in depth* look into how they are implemented under the hood.

As part of the in depth look, I give pseudo-code describing the  main procedures involved in creating and running a blockchain, and also give a executable implementation of a proto-blockchain which can be run on a single or multiple machines. It is a proto-blockchain because it lacks many features like security, scalability etc. necessary for real applications. Indeed, it is purely for pedagogical purposes, but has the basic components that you are likely to see in a full fledged blockchain platform like Ethereum. We chose python as the implementation language partly because of its popularity and simplicity - and partly because I am a researcher/practitioner in AI, where python is the language of choice!

 > **About the reader:** I will assume the reader a) knows/enjoys programming, b) is familiar with some standard computer science (CS) technologies like public/private key cryptography, peer to peer systems etc. and c) prefers to understand things by building them. If you are not such a reader, there are better resources out there for you. An example is the book [1], which I am using as a starting point and reference for these documentation. Another recent exhaustive article is [2]. But of course, you are welcome to follow along for as long as it suits you. But please be warned that if something is a standard piece of CS tech, I will use it without further explanation (but will also try to link to a source that I feel is authoritative).


## Blockchains: A Quick Introduction

The term blockchain itself may refer to at least three different things depending on the context:

1. A peer to peer distributed system that is used to maintain a ledger that is meant to be immutable - that is a peer to peer distributed ledger technology or DLT in short.

2. A linked list like data structure that is used to support the immutability of the ledger in implementations of a DLT.

3. A specific implementation of a DLT.

In the rest of this document, we will give an high level overview what  DLTs are and why we should care about them.

## Peer to peer distributed ledgers

A ledger is a record of a set of transactions of some sort, that grows over time. Ledgers are quite important and ubiquitous in modern life. Examples include ledgers of financial transactions at a shop or a large corporation or a bank, registry of births/deaths/marriages, registry of transfer of land ownership and so on. They are typically maintained by some central trusted (or at least known) authority (like a corporation, a central bank, Department of Land records etc.) which guarantees that information in the ledger can be trusted to a degree and can form the basis of conducting various kinds of business. 

A [peer to peer (P2P)](https://en.wikipedia.org/wiki/Peer-to-peer) distributed ledger (DL) is a digital ledger that is maintained via a peer to peer system with no central trusted authority. This means the ledger only exists in form of electronic bits (the 'digital' part) on various computer systems or **nodes** of equal status, connected via a communications network, like the internet or a private network (the 'peer to peer distributed' part). The ledger records transactions that occur between these nodes (we discuss examples of what these transactions may be in the next subsection). Trust in the contents of the ledger is guaranteed by means of cryptographic tools and clever algorithms (the 'no central trusted authority' part).

Being able to trust the contents of the distributed ledger is of central importance to its use - without trust a DL is useless. There are two main ways trust can be violated. First, a transaction may be added to the ledger without authorization of the node identified as the initiator and  second, the ordering of the transactions may be inconsistent across nodes. Clearly, either of those makes it impossible to use the ledger for conducting busienss.

The first trust issue is solved by having a transaction authorized by (at least) its initiator by [cryptographically signing]() the transaction. This ensures anybody reading the ledger with access to the public key of the intiator can verify the authorization. For example, if each transaction is about transference of ownership, this step ensures that the previous owner authorized the transfer of ownership. During the authorization, it may also be checked that the intiator is actually allowed to carry out the transaction - for instance by checking that a node actually owns the item in question.

The second trust issue is solved by means of a consensus algorithm, called the blockchain consensus algorithm, which uses, among other things, incentives and special properties of the blockchain data structure to ensure that all the nodes in the blockchain maintain a consistent view of the ledger.

> **Indeed this problem of maintaining a globally consistent view of some shared state (the ledger) is a central problem in distributed systems in general, and the main innovation of the blockchain technology is the specific way this is done for distributed ledgers**.

## Blockchain Applications

A P2P DL becomes necessary when either no trusted central authority is available or the central authority currently available is inefficient or costly. An example that is often given is transferring money across international borders. The transfer process is usually quite slow, inefficient and expensive despite the fact that the actual transfer happens digitally. This is primarily because the transfer process is largely centralized and is carried out by a series of large banks in different jurisdictions, each of which take time process their ledgers to reflect the transfer and also charge a fee for their service. 

If the system of money transfer were implemented using a P2P DL then  the transfer would happen directly between the sender and the receiver and would be cost free. Indeed, the inefficiencies of the current financial system was one of the motivating reasons for the invention of the blockchain in the form of the cryptocurrency Bitcoin by the pseudonymous Satoshi Nakamoto [3].

The application of distributed ledgers is limited only by your imagination. Other potential applications include storing medical records securely without trusting any central authority, assuring quality of products from raw materials to delivery, validating authenticity of data being created by IOT devices and so on. At the same time, setting up an effective DL system for an specific application with the right level of security, scalability and flexibility remains a very challenging engineering and design problem, and should not be undertaken lightly. 

Currently, there are an enormous number of blockchain platforms available targeted for specific applications. Example of two platforms designed to support generic use-cases are [Ethereu](https://ethereum.org) and [Substrate](https://substrate.io/). This is **not** an endorsement of either of these -  but merely examples. Please do your own research before selecting one for your use case.

This concludes our brief look at blockchain/distributed ledger technology at a high level. Please refer to [1] or [2] for a much broader look into blockchain technology and its applications.

## Documentation Guide

The rest of the documentation is divided into the following parts:

- [**Preliminaries**](./bc_proto_prelim.md) Some prelimanry topics around hash functions that play an important role in blockchains.

- [**The Blockchain Data Structure**](./bc_proto_blockchain_ds.md) An introduction to the basic components of the blockchain data structure, why they are there.

- [**Merkel Tree**](./bc_proto_merkel_tree.md) A data structure that is often used to store transactions/data within a blockchain, and which provides certain fast validation capabilities.

- [**The Consesus Algorithm**](./bc_proto_consensus_algo.md) The distributed consensus algorithm  that ensures that all the nodes within a blockchain have a consisitent record of the data.

- [**Final Words**](./bc_proto_running_blockchain.md) Some final thoughts on the articles and where to go from here. 

- [** Running Proto-Blockchain**](./bc_proto_running_blockchain.md) Putting together all the components above to get a running proto-blockchain. Discussion of what its limitations are and where to go from here.

All of the above are supported up by pseduocode implementation, and references to python implementaiton in this repo.

I recommend you read the above in sequence.


## References

[1] Drescher, Daniel. *Blockchain Basics: A Non-Technical Introduction in 25 Steps*. Apress, 2017, 1st ed. Edition

[2] Clark, Mitchcell. *Blockchain Explained, Blocks? Chains? How does this whole thing work?* The Verge, Sep 9, 2021, 6:00am EDT. https://www.theverge.com/22654785/blockchain-explained-cryptocurrency-what-is-stake-nft
