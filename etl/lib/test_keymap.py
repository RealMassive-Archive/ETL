import os

from keymap import KeyMap


def test_keymap():
    km = KeyMap()
    km.insert(1234, 'building', 'abcde', 5678, 'building')
    assert km.get_new('building', 'building', 1234) == 5678
    outfile = '/tmp/keymap.csv'
    km.dump(outfile)
    assert os.path.exists(outfile)    
    os.remove(outfile)
