from string import Template

import pyparsing
from blessed import Terminal
from blessed.keyboard import Keystroke, get_keyboard_codes, get_keyboard_sequences


class Keymap:
    """
    A class for managing a set of keymaps: strings that should be turned into keypresses.
    This is mostly useful for special keys presses like <Tab> or <C-v> etc.

    The blessed module is used to lookup key sequences produced by different key presses
    for the current terminal.
    """

    def __init__(self):
        self.mappings = dict()

        t = Terminal()
        sequences = get_keyboard_sequences(t)
        codes = get_keyboard_codes()
        self.keypress_name_to_sequence_mapping = {}
        for c in codes:
            n = codes[c]
            self.keypress_name_to_sequence_mapping[n] = c
        for s in sequences:
            c = sequences[s]
            for n in self.keypress_name_to_sequence_mapping:
                if self.keypress_name_to_sequence_mapping[n] == c:
                    self.keypress_name_to_sequence_mapping[n] = s
        # for k in self.keypress_name_to_sequence_mapping:
        #     v = self.keypress_name_to_sequence_mapping[k]
        #     print(f"{k}:{v!r}")

    def add_mapping(self, k, v):
        if v in self.keypress_name_to_sequence_mapping:
            self.mappings[k] = self.keypress_name_to_sequence_mapping[v]
        else:
            self.mappings[k] = v

    def expand_keymaps(self, text):
        for k in self.mappings:
            v = self.mappings[k]
            text = text.replace(k, v)

        return text
