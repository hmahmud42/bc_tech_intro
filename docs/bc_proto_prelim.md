# Preliminary Notes

In this section we discuss some preliminary issues related to the work.

## A Note on The Pseudocode

All the algorithms and data structures in these articles are written in pseudocode, with pointers to the actual implementation done in python. In writing these series of articles, I had to make a choice about how to write the pseudocode. On the one hand I wanted the documentation to be as programming language agnostic as possible, while on the other I do not want there to be too much of a jump when going from pseudocode to the actual code.

So what I arrived at was a mish-mash of python looking function definitions and C style data structures (so no classes) but with python syntax (!). The pseudocode style is procedural because it is more generic - while the python code is object oriented.  

In choosing the pseudocode syntax I have tried to use what I find most appealing about either - but I am not sure if I have arrived at the best of both worlds, or the worst - I would be interested in hearing from the reader if this works for them!

## Hashing Perliminaries

The properties (A), (B) and (C) of blockchains are achieved through the clever use of hash functions and computationally expensive cryptographic _puzzles_. We now discuss some relevant properties of both.

We discuss some properties of hash functions that are used very heavily in defining blockchains.

### Uniqueness of Hash Functions

[Hash functions](https://en.wikipedia.org/wiki/Hash_function) like [SHA-256](https://en.wikipedia.org/wiki/SHA-2) are very well known concepts in computer science. The blockchain datastructure relies very heavily on the well known "uniqueness property" of these. This property means that given two different strings, say `string-1` and `string-2`, with very high probability, `SHA-256(string-1)` will be different from `SHA-256(string-2)`. You can check this by running the sha256 python function in the python code linked to below on many different strings. Some examples of strings and their (SHA256) hashes are given below.

```python
"blockchain" "ef7797e13d3a75526946a3bcf00daec9fc9c9c4d51ddc7cc5df888f74dd434d1"
"Hello World" "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
"Quick Brown Fox" "0a3f5db66fadecb57247516e43d8a3572f3927a4871bca6469ee5a6fb3022041"

```

It is important to understand that it is generally safe to assume that the probability of _collision_ (that is two different strings having the same hash) in practice is `0`. For instance for SHA-256 the collision probability is `1.47*10^(-29)` - roughly the same as flipping a fair coin and getting `~97` heads in a row, a practical impossibility. If for any reason you are not happy with this probability, you can always switch to a hash function with a even smaller collision probability, at the cost of higher computational cost.

The reason the uniqueness property is useful is that, for long strings (like some piece of data), the hash acts like a thumbprint or a signature which we can store without needing to store the string itself. If subsequently we are presented with a string which is being claimed as the original string, we can calculate the hash of the new string and compare with the stored hash to validate this claim. This property will come in very handy below.

### Cryptographic Puzzles

Crypotgraphic hash puzzles are used to to make it difficult to tamper with a blockchain data structure. The main property of these puzzles that is used is that they are very computationally expensive to solve and computationally very cheap to verify. These puzzles are based on the so-called _one-way_ property of hash functions which is that given the hash of a particular string it is not possible to compute what the original string was without actually systematically going through all possible strings and checking which string matches the given hash string. Given this, the puzzle is defined as follows.

We are given a string `s` for which we create the puzzle. The puzzle has an associated difficulty level `d` which is a positive whole number. Given a hash function `hash` the puzzl is to find the number `n` such that `hash(sn)` is starts with `d` zeros. The following pseudocode shows how to solve this puzzle and then how to verify a solution:
```python
def solve_puzzle(s: str, d: int) -> str:
    nonce = 0
    prefix = repeat('0', d) # a string with d 0s
    h = hash(s + str(nonce)) # '+' = concatenate
    while h[0:d] != prefix:
        nonce = nonce + 1
        h = hash(s + str(nonce))
    return str(nonce)


def check_solution(s: str, nonce:str , d:int) -> str:
    prefix = repeat('0', d) # a string with d 0s
    return hash(s + str(nonce))[0:d] == prefix
```

The following shows some strings and the corresponding nonces using the SHA256 function at difficulty level 2.
```python
"blockchain" 263
"Hello World" 135
"Quick Brown Fox" 29
```
