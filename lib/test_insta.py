from insta import Sequence, next_id

def test_next_id():
    seq = Sequence()
    assert len(str(next_id(seq))) == 19
