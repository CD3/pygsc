from pathlib import Path


class Script:
  def __init__(self,filename=None):
    self.filenames = []
    self.lines = []
    self.add_lines(filename)
    self.line = 0
    self.col = 0

  def eol(self):
    return self.line >= len(self.lines) or self.col >= len(self.lines[self.line])

  def eof(self):
    return self.line >= len(self.lines) or (self.line >= len(self.lines)-1 and self.col >= len(self.lines[self.line]))

  def add_lines(self,lines):

    if isinstance(lines,str):
      lines = Path(lines)

    if isinstance(lines,Path):
      self.filenames = str(lines)
      lines = lines.read_text().split("\n")
    else:
      self.filenames = "None"

    self.lines += lines

  def seek_next_line(self,n=1,ret=True):
    self.line += n
    self.line = min(self.line,len(self.lines))
    if ret:
      self.reset_seek_col()

  def seek_prev_line(self,n=1,ret=True):
    self.line -= n
    self.line = max(self.line,0)
    if ret:
      self.reset_seek_col()

  def seek_next_col(self,n=1):
    self.col += n
    self.col = min(self.col,len(self.current_line("")))

  def seek_prev_col(self,n=1):
    self.col -= n
    self.col = max(self.col,0)

  def seek_end_col(self):
    self.col = len(self.current_line(""))

  def seek_beg_col(self):
    self.col = 0

  def iter_lines(self):
    while self.line < len(self.lines):
      self.line += 1
      yield self.lines[self.line-1]

  def iter_chars_on_current_line(self):
    while self.line < len(self.lines) and self.col < len(self.lines[self.line]):
      self.col += 1
      yield self.lines[self.line][self.col-1]



  def current_line(self,return_on_out_of_range=None):
    N = len(self.lines)
    if self.line >= N or self.line < 0:
      return return_on_out_of_range
    return self.lines[self.line]

  def current_char(self):
    return self.lines[self.line][self.col]
      
  def reset_seek_line(self):
    self.line = 0

  def reset_seek_col(self):
    self.col = 0

  def reset_seek(self):
    self.reset_seek_line()
    self.reset_seek_col()






