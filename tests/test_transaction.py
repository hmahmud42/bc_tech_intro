"""
Tests for the classes Transaction and TransactionManager.
"""
from collections import defaultdict
from blockchain_proto.consts import TRANS_NO, USER_ID, TRANS_STR
from blockchain_proto.puzzle import sha_256_hash_string
from blockchain_proto.transaction import Transaction, TransactionManager


def test_transaction():
    # test creation
    try:
        tr1 = Transaction(user_id="User 1",
                          trans_no=23,
                          trans_str="P" * 70)
    except AssertionError as e:
        pass
    else:
        assert False

    # test validation
    tr1 = Transaction(user_id="User 1",
                      trans_no=23,
                      trans_str="P")
    tr1.trans_str = "P" * 70
    assert not tr1.validate()
    tr1.trans_str = "Pay Bob 23 Gold coins"

    # test ordering
    tr2 = Transaction(user_id="User 1",
                      trans_no=24,
                      trans_str="Pay Bob 23 Gold coins")
    assert tr2.validate()

    tr3 = Transaction(user_id="User 1",
                      trans_no=23,
                      trans_str="Pay Bob 23 Gold coins")
    assert tr1 == tr3

    tr4 = Transaction(user_id="User 2",
                      trans_no=1,
                      trans_str="Pay Bob 23 Gold coins")

    assert tr1 < tr2 and tr3 < tr2
    assert tr1 < tr4 and not tr1 == tr4
    assert tr2 < tr4

    # test conversion to json
    tr_json = tr1.to_json()
    for key in [USER_ID, TRANS_NO, TRANS_STR]:
        assert key in tr_json

    assert tr_json[USER_ID] == "User 1" and \
        tr_json[TRANS_NO] == 23 and \
        tr_json[TRANS_STR] == "Pay Bob 23 Gold coins"

    assert str(tr1) == "User 1 23 Pay Bob 23 Gold coins"

    # test hashing
    tr_strs = [
        "User 1 23 Pay Bob 23 Gold coins",
        "User 1 24 Pay Bob 23 Gold coins",
        "User 1 23 Pay Bob 23 Gold coins",
        "User 2 1 Pay Bob 23 Gold coins"
    ]
    hashes = sha_256_hash_string("".join(tr_strs))
    assert Transaction.get_trans_hash([tr1, tr2, tr3, tr4]) == hashes


def test_transaction_manager_add():

    trans_manager = TransactionManager()

    # test basic addition
    tr1 = Transaction(user_id="User 1",
                      trans_no=23,
                      trans_str="Pay Bob 23 Gold coins")
    tr2 = Transaction(user_id="User 1",
                      trans_no=22,
                      trans_str="Pay Bob 22 Gold coins")

    trans_manager.add_transaction(tr1)
    trans_manager.add_transaction(tr2)

    # test double addition
    tr1_dup = Transaction(user_id="User 1",
                          trans_no=23,
                          trans_str="Pay Bob 23 Gold coins")

    try:
        trans_manager.add_transaction(tr1_dup)
    except ValueError as ve:
        pass
    else:
        assert False


def test_transaction_manager_get_valid():
    # test getting valid transactions.
    trans_manager = TransactionManager()
    num_user = 4
    user_trans = []
    num_trans = [12, 10, 11, 22]
    base_trans_nos = [12, 13, 24, 55]
    for user in range(num_user):
        # transactions to be returned
        user_trans.append([
            Transaction(user_id=f"User {user}",
                        trans_no=trans_no,
                        trans_str=f"Pay Bob {trans_no} Gold coins")
            for trans_no in range(base_trans_nos[user],
                                  base_trans_nos[user] + num_trans[user])
        ])
        # older transactions should not be returned
        user_trans[user].extend(
            Transaction(user_id=f"User {user}",
                        trans_no=trans_no,
                        trans_str=f"Pay Bob {trans_no} Gold coins")
            for trans_no in range(base_trans_nos[user] - 3,
                                  base_trans_nos[user])

        )
        # new, out of sequence transactions, should not be returned
        user_trans[user].extend(
            Transaction(user_id=f"User {user}",
                        trans_no=trans_no,
                        trans_str=f"Pay Bob {trans_no} Gold coins")
            for trans_no in range(base_trans_nos[user] + num_trans[user] + 1,
                                  base_trans_nos[user] + num_trans[user] + 10,
                                  2)

        )

    for user in range(num_user):
        for tr in user_trans[user]:
            trans_manager.add_transaction(tr)

    last_trans_dict = {f"User {user}": base_trans_nos[user]-1 for user in range(num_user-1)}

    valid_trans = trans_manager.get_valid_trans(last_trans_dict)

    ret_trans = defaultdict(lambda : [])
    for tr in valid_trans:
        ret_trans[tr.user_id].append(tr)

    # test excluding user who is not in the fork, and whose
    # initial sequence has not yet been received at the node.
    assert f"User {num_user}" not in ret_trans
    assert len(ret_trans) == num_user - 1

    # check only the valid transactions are returned and
    # sorted by trans no
    for user in range(num_user-1) :
        tr_nos = [tr.trans_no for tr in ret_trans[f"User {user}"]]
        assert tr_nos == list(range(base_trans_nos[user],
                                    (base_trans_nos[user] + num_trans[user])))


if __name__ == '__main__':
    test_transaction()
    test_transaction_manager_add()
    test_transaction_manager_get_valid()