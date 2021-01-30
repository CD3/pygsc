from pygsc.Script import Script
from pygsc import ucode
import pytest 
import os
from utils import tmpfile


@pytest.fixture
def simple_script():
  file = tmpfile(["ls","pwd","date"])
  return Script(file)


def test_line_iteration(simple_script):
  script = simple_script

  lgen = script.iter_lines()

  assert next(lgen) == "ls"
  assert next(lgen) == "pwd"
  assert next(lgen) == "date"
  with pytest.raises(StopIteration):
    next(lgen)

  script.reset_seek_line()

  lgen = script.iter_lines()

  assert next(lgen) == "ls"
  assert next(lgen) == "pwd"
  assert next(lgen) == "date"
  with pytest.raises(StopIteration):
    next(lgen)


def test_line_seeking(simple_script):
  script = simple_script

  lgen = script.iter_lines()

  lgen = script.iter_lines()
  assert next(lgen) == "ls"
  script.seek_next_line()
  assert next(lgen) == "date"
  script.reset_seek_line()
  assert next(lgen) == "ls"
  assert next(lgen) == "pwd"
  script.seek_prev_line()
  assert next(lgen) == "pwd"
  script.seek_prev_line(2)
  assert next(lgen) == "ls"
  script.seek_next_line(1)
  assert next(lgen) == "date"
  script.seek_prev_line(10)
  assert next(lgen) == "ls"
  script.seek_next_line(10)
  with pytest.raises(StopIteration):
    next(lgen)



def test_char_iteration(simple_script):
  script = simple_script
  cgen = script.iter_chars_on_current_line()

  assert next(cgen) == "l"
  assert next(cgen) == "s"
  with pytest.raises(StopIteration):
    next(cgen)
  assert script.eol()
  assert not script.eof()


def test_char_seeking(simple_script):
  script = simple_script
  script.seek_next_line()

  cgen = script.iter_chars_on_current_line()
  assert next(cgen) == "p"
  assert next(cgen) == "w"
  script.seek_prev_col()
  assert next(cgen) == "w"
  assert next(cgen) == "d"
  with pytest.raises(StopIteration):
    next(cgen)
  assert script.eol()
  assert not script.eof()


  script.seek_next_line()

  cgen = script.iter_chars_on_current_line()
  assert next(cgen) == "d"
  assert next(cgen) == "a"
  assert next(cgen) == "t"
  assert next(cgen) == "e"
  with pytest.raises(StopIteration):
    next(cgen)
  assert script.eol()
  assert script.eof()


  script.seek_next_line()
  script.reset_seek_col()
  cgen = script.iter_chars_on_current_line()

  with pytest.raises(StopIteration):
    next(cgen)
  assert script.eol()
  assert script.eof()

def test_current_char_with_seeking(simple_script):
  script = simple_script

  assert script.current_char() == 'l'
  assert script.current_char() == 'l'
  script.seek_next_col()
  assert script.current_char() == 's'
  script.seek_next_col()
  assert script.eol()
  assert not script.eof()



  script.seek_next_line()

  assert script.current_char() == 'p'
  script.seek_next_col()
  assert script.current_char() == 'w'
  script.seek_next_col()
  assert script.current_char() == 'd'
  script.seek_next_col()
  assert script.eol()
  assert not script.eof()



  script.seek_next_line(ret=False)
  assert script.current_char() == 'e'
  script.seek_prev_col()
  assert script.current_char() == 't'
  script.seek_prev_line(ret=False)
  assert script.current_char() == 'd'
  script.seek_next_col()
  assert script.eol()
  assert not script.eof()

  script.seek_next_line()

  assert script.current_char() == 'd'
  script.seek_next_col()
  assert script.current_char() == 'a'
  script.seek_next_col()
  assert script.current_char() == 't'
  script.seek_next_col()
  assert script.current_char() == 'e'
  script.seek_next_col()
  assert script.eol()
  assert script.eof()


def test_script_rendering():
  file = tmpfile(["x%{var1}x","%{HOME}/tmp"])
  script = Script(file)
  script.render({"var1":"val1"})

  assert script.lines[0] == "xval1x"
  assert script.lines[1] == "%{HOME}/tmp"

  script.render(os.environ)

  assert script.lines[0] == "xval1x"
  assert script.lines[1] == f"{os.environ['HOME']}/tmp"

