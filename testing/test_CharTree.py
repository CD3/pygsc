from pygsc.CharTree import CharTree
from pygsc import ucode
import pytest 


def test_devel():
  t = CharTree()
  t.add_char('a')
  t.add_char('c')
  t['a'].add_char('c')
  t['a'].add_char('l')
  t['a']['c'].add_char('t')


  assert len(t.chars) == 2
  assert len(t.chars['a'].chars) == 2
  assert len(t.chars['a'].chars['c'].chars) == 1

  assert len(t.chars['a']) == 2
  assert len(t.chars['a'].chars['c']) == 1

  assert len(t['a']) == 2
  assert len(t['a']['c']) == 1

  assert t['a']['c']['t'].get_prefix() == 'act'
  assert t['a']['c']['t'].get_string() == 'act'
  assert t['a']['c']['t'].get_string('b') == 'actb'
  assert t['act'].get_string('b') == 'actb'

  t.add_sequence('abcdefg')
  assert t['abcdefg'].get_string('b') == 'abcdefgb'



def test_matching():

  t = CharTree()
  t.add_sequence('cat')
  t.add_sequence('cats')
  t.add_sequence('dogs')
  t.add_sequence('call')


  assert t.match("cats and dogs") == "cats"
  assert t.match("cat and dog") == "cat"
  assert t.match("call your cat") == "call"
  assert t.match("keep your dogs inside") is None
  assert t.match("cal is warm") is None
  assert t.match("ca should not match") is None

