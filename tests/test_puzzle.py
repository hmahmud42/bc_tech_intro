"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Tests for puzzle related functions.
"""
from numpy.random import choice
import string
from blockchain_proto.blockchain.puzzle import *


def test_puzzle():
    letters = [c for c in string.ascii_letters]
    diff = 2
    for i in range(10):
        random_string = ''.join(choice(letters, size=100))
        nonce = solve_puzzle(random_string, diff)
        assert check_solution(random_string, str(nonce), diff)

    nonce = solve_puzzle("Hello World", diff)
    sol_hash = sha_256_hash_string("Hello World" + str(nonce))
    assert sol_hash[0:diff] == '0' * diff
    assert check_solution("Hello World", str(nonce), diff)


if __name__ == '__main__':
    test_puzzle()
