from pygsc.CommandParser import CommandParser
from pygsc import ucode
import pytest 


def test_basic_commands():
  parser = CommandParser()

  if parser.have_pyparsing:
    parser.add_command("no_arg_command")
    parser.add_command("one_arg_command")
    parser.add_command("two_arg_command")

    result = parser.parse("# no_arg_command")
    assert result is not None
    assert result['name'] == "no_arg_command"
    assert result['args'] == ""

    result = parser.parse("#  one_arg_command: off")
    assert result is not None
    assert result['name'] == "one_arg_command"
    assert result['args'][0] == "off"

    result = parser.parse("# one_arg_command: 'off'")
    assert result is not None
    assert result['name'] == "one_arg_command"
    assert result['args'][0] == "off"

    result = parser.parse("# one_arg_command: 'off and on'")
    assert result is not None
    assert result['name'] == "one_arg_command"
    assert result['args'][0] == "off and on"

    result = parser.parse("# two_arg_command: arg1 'arg 2' ")
    assert result is not None
    assert result['name'] == "two_arg_command"
    assert result['args'][0] == "arg1"
    assert result['args'][1] == "arg 2"

def test_basic_commands():
  parser = CommandParser()

  if parser.have_pyparsing:
    parser.add_command("primary",['alias1','alias 2'])

    result = parser.parse("# primary")
    assert result is not None
    assert result['name'] == "primary"

    result = parser.parse("# alias1")
    assert result is not None
    assert result['name'] == "primary"

    result = parser.parse("#  alias 2")
    assert result is not None
    assert result['name'] == "primary"
