from blockchain_proto.consts import TRANS_NO, USER_ID, TRANS_STR
from blockchain_proto.puzzle import sha_256_hash_string
from blockchain_proto.transaction import Transaction


def test_transaction():

    try:
        tr1 = Transaction(user_id="User 1",
                          trans_no=23,
                          trans_str="P" * 70)
    except AssertionError as e:
        pass
    else:
        assert False

    tr1 = Transaction(user_id="User 1",
                      trans_no=23,
                      trans_str="P")
    tr1.trans_str = "P" * 70
    assert not tr1.validate()
    tr1.trans_str = "Pay Bob 23 Gold coins"

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

    tr_json = tr1.to_json()
    for key in [USER_ID, TRANS_NO, TRANS_STR]:
        assert key in tr_json

    assert tr_json[USER_ID] == "User 1" and \
        tr_json[TRANS_NO] == 23 and \
        tr_json[TRANS_STR] == "Pay Bob 23 Gold coins"

    assert str(tr1) == "User 1 23 Pay Bob 23 Gold coins"

    tr_strs = [
        "User 1 23 Pay Bob 23 Gold coins",
        "User 1 24 Pay Bob 23 Gold coins",
        "User 1 23 Pay Bob 23 Gold coins",
        "User 2 1 Pay Bob 23 Gold coins"
    ]
    hashes = sha_256_hash_string("".join(tr_strs))
    assert Transaction.get_trans_hash([tr1, tr2, tr3, tr4]) == hashes


if __name__ == '__main__':
    test_transaction()