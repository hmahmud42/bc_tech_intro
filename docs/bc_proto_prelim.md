# Preliminary Notes

In this section we discuss some background concepts that will be useful later on. 

## A Note on The Pseudocode

All the algorithms and data structures in these articles are written in pseudocode, with pointers to the actual implementation in python. The pseudocode style used here is somewhat unique. It is a mixture of python-esque function definitions and C-style `structs` (so no classes) written with a python syntax. The reason for this choice was to balance making the presentation as language agnostic as possible (hence procedural rather than object oriented style of coding), and make the jump to python code less jarring. We would be interested in hearing from the reader if this works for them, and if not what they would suggest.

## Hashing Preliminaries

In this section discuss some properties of hash functions that are used very heavily in defining blockchains. 

### Uniqueness of Hash Functions

[Hash functions](https://en.wikipedia.org/wiki/Hash_function) like [SHA-256](https://en.wikipedia.org/wiki/SHA-2) are well known concepts in computer science. The blockchain data structure relies very heavily on the "uniqueness property" of these functions. This property means that given two different strings, say `string-1` and `string-2`, with _very high probability_, `SHA-256(string-1)` will be different from `SHA-256(string-2)`. You can check this by running the sha256 python function in the python code [here](../blockchain_proto/puzzle.py#L12) on many different strings. Some examples of strings and their (SHA256) hashes are given below.

```python
"blockchain" "ef7797e13d3a75526946a3bcf00daec9fc9c9c4d51ddc7cc5df888f74dd434d1"
"Hello World" "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
"Quick Brown Fox" "0a3f5db66fadecb57247516e43d8a3572f3927a4871bca6469ee5a6fb3022041"
```

It is important to understand that it is generally safe to assume that the probability of _collision_ (that is two different strings having the same hash) in practice is `0`. For instance for SHA-256 the collision probability is `1.47*10^(-29)` - roughly the same as flipping a fair coin and getting `~97` heads in a row, a practical impossibility. If for any reason you are not happy with this probability, you can always switch to a hash function with a even smaller collision probability, at the cost of higher computational cost.

The reason the uniqueness property is useful is that, for long strings (like some piece of data), the hash acts like a thumbprint or a signature which we can store without needing to store the string itself. If subsequently we are presented with a string which is being claimed as the original string, we can calculate the hash of the new string and compare with the stored hash to validate this claim. This property will come in very handy below.

### Cryptographic Puzzles

Cryptographic hash puzzles are used to to make it difficult to tamper with a blockchain data structure. The main property of these puzzles that is used is that they are very computationally expensive to solve and computationally very cheap to verify. These puzzles are based on the so-called _one-way_ property of hash functions. This property states that given the hash of a particular string, it is not possible to recover that string from the hash without systematically checking the hash of all possible strings (for instance, by lexicographical order). Given this, the puzzle is defined as follows.

Given a hash function `hash`, the puzzle is defined for a string `s` and a difficulty level `d`, which is a positive whole number: _Find the number `n` such that `hash(sn)` is starts with `d` zeros._ 

The following pseudocode shows how to solve this puzzle by systematically trying all possible extensions of the string `s`:
```python
def solve_puzzle(s: str, d: int) -> str:
    nonce = 0
    prefix = repeat('0', d) # a string with d 0s
    h = hash(s + str(nonce)) # '+' = concatenate
    while h[0:d] != prefix:
        nonce = nonce + 1
        h = hash(s + str(nonce))
    return str(nonce)
```

The following pseudocode shows how to check that a solution is valid:

```python
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
You can check this by opening a (i)python terminal and copying and trying the functions defined [here](../blockchain_proto/puzzle.py).

We note here that solving a computationally expensive puzzle is often referred to as **mining** or creating a **proof of work** in the context of blockchains. It is likely you have heard of these terms often.
