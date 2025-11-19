import pytest
from blessed import Terminal
from blessed.keyboard import Keystroke, get_keyboard_codes, get_keyboard_sequences

from pygsc.Keymap import Keymap


def test_creating_keymap():
    keymap = Keymap()

    keymap.add_mapping("<Tab>", "	")
    keymap.add_mapping("<Esc>", "")
    keymap.add_mapping("<C-v>", "")

    text = keymap.expand_keymaps("<Tab> and <Esc>")
    assert text == "	 and "
    assert text == "\t and \x1b"


def test_creating_keymap_using_term_names():
    keymap = Keymap()

    keymap.add_mapping("<Tab>", "KEY_TAB")
    keymap.add_mapping("<Esc>", "KEY_ESCAPE")

    text = keymap.expand_keymaps("<Tab> and <Esc>")
    assert text == "	 and "
    assert text == "\t and "
