Copyright 2022 M. M. Hassan Mahmud

# Blockchains: A Quick Introduction

In this article, we cover at a high level what blockchains are and what kind of applications they are useful for they are useful for about and so forth. The word blockchain itself can mean at least a couple of different things. It can refer to

1. A *peer to peer distributed ledger* (see below).

2. A specific implementation of of (1) (like Ethereum).

3. A new kind of linked-list type data structure where each element is a 'block' of cryptographically encoded data. This is used to implement (1).

4. Algorithm and methods that use (3) to maintain specific instances of a P2P distributed ledger.



In the following we will quickly unpack the first meaning and giving some examples of the second meaning. The rest of the articles in this repo will go into (3) and (4() in depth. 


## Peer to peer distributed ledgers

A ledger is a set of transactions of some sort that grows over time. Ledgers are quite important and ubiquitous in modern life. Examples include ledgers of financial transactions at a shop or a large corporation or a bank, registry of births/deaths/marriages, registry of transfer of land ownership and so on. They are typically maintained by some central trusted (or at least known) authority (like a corporation, a central bank, Department of Land records etc.). This authority guarantees that the information in the ledger can be trusted to a degree and form the basis of conducting various kinds of business. 

A [peer to peer (P2P)](https://en.wikipedia.org/wiki/Peer-to-peer) distributed ledger is a *digital ledger that is maintained via a peer to peer system with no central trusted authority*. This means that the ledger only exists in form of electronic bits (the 'digital' part) on various computer systems or **nodes** of equal status. These nodes are connected via a communications network, like the internet or a private network (the 'peer to peer distributed' part). The ledger records *transactions* that occur between users of these nodes (so each node can support multiple users). We discuss examples of what these transactions may be in the next subsection. Trust in the contents of the ledger is guaranteed by means of cryptographic tools and clever algorithms (the 'no central trusted authority' part). 

Being able to trust the contents of the distributed ledger is of central importance to its use. There are two main ways trust can be violated. 
- First, a transaction may be added to the ledger without authorization of the node identified as the initiator.
  - This means that, for instance, nodes are able to transfer ownership of items or funds/money from their owners at will.
- Second, the ordering of the transactions may be inconsistent across nodes. 
  - This means that, for instance, nodes may not agree on who owns a particular item or sum of money  or when the transfer of ownership happend.

Either of these make it impossible to use the ledger for conducting business. 

The first trust issue is solved by having a transaction authorized by (at least) its initiator by [cryptographically signing](https://en.wikipedia.org/wiki/Digital_signature) the transaction. This ensures anybody reading the ledger with access to the public key of the initiator can verify the authorization. For example, if each transaction is about transference of ownership, this step ensures that the previous owner authorized the transfer of ownership. During the authorization, it may also be checked that the initiator is actually allowed to carry out the transaction - for instance by checking that a node actually owns the item in question.

The second trust issue is solved by means of the the _blockchain consensus algorithm_. This algorithm uses various incentives and special properties of the blockchain data structure to ensure that all the nodes in the blockchain maintain a consistent view of the ledger. 
The documentation in this repo gives a technical introduction to how this second trust issue is solved.

> **The problem of maintaining a globally consistent view of some shared state (the ledger in the case of blockchains) is a central problem in distributed systems in general. The main innovation of the blockchain technology is the specific way this is done for distributed ledgers**.


## Blockchain Applications

A P2P DL becomes necessary or useful when either no trusted central authority is available, or the central authority currently available is inefficient or costly. An oft cited example is the problem of transferring money across international borders. The transfer process is usually quite inefficient and expensive despite the fact that the actual transfer happens digitally. The transfer process is largely centralized and is carried out by a series of large banks in different jurisdictions. The inefficiency is direct result of each bank needing to process the transfer in their slow legacy systems. The high cost is a result of each bank charging a fee to process the transaction. 

If instead the transfer is recorded using a blockchain, then it would happen directly between the sender and the receiver and hence would be fast and cost free. Indeed, the inefficiencies of the current financial system motivated the invention of the blockchain in the form of the [cryptocurrency Bitcoin](https://en.wikipedia.org/wiki/Bitcoin) by the pseudonymous Satoshi Nakamoto [3].

In principle, any application where a central record or ledger is used can be transformed to use a blockchain instead. For instance blockchains can be used to store medical records securely without trusting any central authority, record movement of goods in a supply chain in a trusted and verified way, validate authenticity of data generated by IOT devices and so on. At the same time, setting up an effective blockchain for an specific application with the right level of security, scalability and flexibility remains a  very challenging engineering and design problem. As always, the business case has to be fleshed out and justified before a blockchain based solution is adopted. 

Currently, there are an enormous number of blockchain platforms available targeted for specific applications. Example of two platforms designed to support generic use-cases are [Ethereum](https://ethereum.org), [Substrate](https://substrate.io/) and [Cardano](https://cardano.org/). This is **not** an endorsement of either of these -  but merely examples. Platforms for specific applications should be chosen after due consideration of use-case requirements and platform capabilities.

## Next Steps

This concludes our brief look at blockchain/distributed ledger technology at a high level. Please refer to [1] or [2] for a much broader look into blockchain technology and its applications. The [next article](./bc_proto_prelim.md) in the series covers some preliminary concepts as preparation for our deep technical dive into how blockchains are implemented. 


## References

[1] Drescher, Daniel. *Blockchain Basics: A Non-Technical Introduction in 25 Steps*. Apress, 2017, 1st ed. Edition

[2] Clark, Mitchcell. *Blockchain Explained, Blocks? Chains? How does this whole thing work?* The Verge, Sep 9, 2021, 6:00am EDT. https://www.theverge.com/22654785/blockchain-explained-cryptocurrency-what-is-stake-nft

[3] Nakamoto, Satoshi. Bitcoin: A Peer-to-Peer Electronic Cash System. 2008. https://www.ussc.gov/sites/default/files/pdf/training/annual-national-training-seminar/2018/Emerging_Tech_Bitcoin_Crypto.pdf

<br>
<hr>

[Next Article: Preliminaries](./bc_proto_prelim.md)
