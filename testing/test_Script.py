from pygsc.Script import Script
import tempfile
import pytest

def tmpfile(lines):
  if isinstance(lines,str):
    lines = [lines]

  file = tempfile.NamedTemporaryFile(delete=False)
  file.write('\n'.join(lines).encode('utf-8'))
  file.close()

  return file.name



def test_looping_through_script():

  file = tmpfile(["ls","pwd","date"])

  script = Script(file)

  lgen = script.iter_lines()

  assert next(lgen) == "ls"
  assert next(lgen) == "pwd"
  assert next(lgen) == "date"
  with pytest.raises(StopIteration):
    next(lgen)

  script.reset_seek_line()

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

  script.reset_seek()


  cgen = script.iter_chars_on_current_line()

  assert next(cgen) == "l"
  assert next(cgen) == "s"
  with pytest.raises(StopIteration):
    next(cgen)
  assert script.eol()
  assert not script.eof()

  script.seek_next_line()
  script.reset_seek_col()

  cgen = script.iter_chars_on_current_line()
  assert next(cgen) == "p"
  assert next(cgen) == "w"
  assert next(cgen) == "d"
  with pytest.raises(StopIteration):
    next(cgen)
  assert script.eol()
  assert not script.eof()


  script.seek_next_line()
  script.reset_seek_col()

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



  script.reset_seek()
  assert script.current_char() == 'l'
  assert script.current_char() == 'l'
  script.seek_next_char()
  assert script.current_char() == 's'
  script.seek_next_char()
  assert script.eol()
  assert not script.eof()



  script.seek_next_line()

  assert script.current_char() == 'p'
  script.seek_next_char()
  assert script.current_char() == 'w'
  script.seek_next_char()
  assert script.current_char() == 'd'
  script.seek_next_char()
  assert script.eol()
  assert not script.eof()



  script.seek_next_line()

  assert script.current_char() == 'd'
  script.seek_next_char()
  assert script.current_char() == 'a'
  script.seek_next_char()
  assert script.current_char() == 't'
  script.seek_next_char()
  assert script.current_char() == 'e'
  script.seek_next_char()
  assert script.eol()
  assert script.eof()



