# Final Words

In this section we end this series of articles with some final words on some additional topics that I feel are useful to know about. 

## Smart Contracts

One really interesting innovation in the space of blockchains has been so called smart contracts. The explanation of [Ethereum Smart Contracts](https://ethereum.org/en/developers/docs/smart-contracts/)) is really well done and easy to understand so I recommend you read that. But very briefly, this is what they are. 

A Smart contract are special kinds of transactions. They are added to the blockchain by nodes/users the same as normal transactions. But once added, they can be _executed_ by users of the blockchain. They can be executed because they are in fact fully fledged programs, written in a language specific to the blockchain platform. The program, when invoked by a user will automatically generate one or more transactions and add them to the blockchain. Depending on the specific platform, a smart contract may need to have resources associated with it so that. Regardless, the really interesting thing about these are that they open up completely new ways of developing  applications on blockchain.


## Public Vs. Private, Permissionsed Blockchains

The specific blockchain technology that we have talked about so far are public blockchains, meanining that any body in the world at all can add transactions to it and no one in the chain can be trusted. In many ways, this is the most extreme version of blockchains and distributed systems in general. For many applications, a private, permissioned blockchain may be more appropriate. As the name implies, a private blockchain can only be joined by invitation and mechanisms other than proof of work consensus may be used to write blocks into the chain. Roughly speaking, tradeoff here is between possibly more efficient and secure (provided you trust the entities in charge) blockchain, at the loss of decentralization. A starting point for undertanding the difference is [here](https://www.blockchain-council.org/blockchain/public-vs-private-blockchain-a-comprehensive-comparison/), but this is another vast area and you need to do the necessary research for any specific use case you may have in mind.


## Alternatives to Proof of Work

To recap, the consenus algorithm we have described in these set of articles is based on proof of work (PoW) - which just refers to the fact that in order to add blocks to the chain, the nodes need to solve a computationally expensive puzzle. This in turn combines with the reward mechanism to help ensure that a consensus is reached in a blockchain. While PoW is effective in ensuring consensus, it also has signficant cons. 

One really big con is that it results in a lot emmissions due to the computational effort invovled. Additionally the blockchain itself is not particularly efficient as adding transactions to the ledger requires requires solving the puzzle takes up time. Another con is that PoW can lead to centralization in the blockchain as nodes/miner with massive computational power can come to dominate the blockchain.

Because of these reasons blockchain designers have been studying alternatives to proof of work algorithms. Some prominent examples of these include proof of stake and proof of reputation, where nodes get the right to write a block based on, respectivley, how much stake they have in the blockchain (measured by accumulation of some token associated with the chain) or based on their reputation, where the reputation of a node is determined by some pre-determined central entity and kept up to date. Obviously, in solving the cons of PoW, these introduce their own issues - for example, losing the centralized character of blockchains. This is another vast topic in its own right (are you seeing a pattern here?) and a starting point for further understanding is [1].



## Conclusion 

 At the same time, Blockchain is a vast topic, with billions of dollars invested, new platforms coming online all the time, targeted towards different applications, with new capabilities along with academic research being conducted to understand the nature of these systems. The goal of these breif series of artcles was to give the reader a concrete and technical introduction to blockchain technology, which can serve as starting point for having a substantive understanding of this technology, which seems set to have a significant impact in the future.


## References

 [1] Ferdous, Md Sadek and Chowdhury, Mohammad Jabed Morshed and Hoque, Mohammad A. and Colman, Alan. Blockchain Consensus Algorithms: A Survey. arXiv:2001.07091. https://arxiv.org/abs/2001.07091
