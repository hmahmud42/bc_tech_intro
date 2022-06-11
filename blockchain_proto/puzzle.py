"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Some utility functions for dealing with puzzles.
"""
from typing import Callable
import _hashlib
from hashlib import sha256
from functools import reduce


def concat_strs(str_list: [str]) -> str:
    return reduce(lambda x, y: x + y, str_list, "")


def sha_256_hash_string(s: str) -> str:
    """
    Returns the hashstring for the given string using hash_func 
    from the hashlib package.

    Parameters
    ----------
    s: str
        The string to create the hash for
    """
    return sha256(s.encode('utf-8')).hexdigest()


def solve_puzzle(s: str, d: int) -> int:
    """
    Solves the following puzzle: what is an int which when 
    stringified and concatenated to the end of s results in 
    a SHA-256 hash with d `0`s in the front.

    Parameters
    ----------

    s: str
        The string to solve the puzzle for

    d: int
        The difficulty level of the puzzle.

    Returns
    -------
    int: 
        The solution to the puzzle.
    """
    nonce = 0
    prefix = '0' * d 
    h = sha_256_hash_string(s + str(nonce))
    while h[0:d] != prefix:
        nonce = nonce + 1
        h = sha_256_hash_string(s + str(nonce))
    return nonce


def check_solution(s: str, nonce: str , d: int) -> bool:
    """
    Verifies that nonce is a solution to the puzzle solved
    by solve_puzzle(s, d)

    Parameters
    ----------

    s: str
        The string to solve the puzzle for

    nonce: int
        The solution to the puzzle.

    d: int
        The difficulty level of the puzzle.

    Returns
    -------
    bool: 
        True if the nonce is a solution, Fals otherwise
    """
    prefix = '0' * d # a string with d 0s
    return sha_256_hash_string(s + str(nonce))[0:d] == prefix
