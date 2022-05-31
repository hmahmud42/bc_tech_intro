from numpy.random import choice
import string
from blockchain_proto.puzzle import *


def test_concat():
    str_list = ["In ", "the ", "beginning ", "was ", "the ", "chain"]
    assert "In the beginning was the chain" == concat_strs(str_list)


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
    test_concat()
    test_puzzle()
