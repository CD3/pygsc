import sys,tty,string
from collections import deque
import io
from .TerminalSession import *

class ScriptRecorder:

  def __init__(self,shell):
    self.shell = shell
    self.STDINFD = sys.stdin.fileno()
    self.exit_flag = False
    self.terminal = TerminalSession(self.shell)
    self.saved_terminal_settings = None
    self.lines = []

  def cleanup(self):
      try:
        self.terminal.stop()
      except: pass

      try:
        termios.tcsetattr(self.STDINFD, termios.TCSANOW, self.saved_terminal_settings)
      except: pass

  def get_bytes(self):
    return b'\n'.join(self.lines)

  def run(self):
    
    self.saved_terminal_settings = termios.tcgetattr(self.STDINFD)
    tty.setraw(self.STDINFD)

    def add_line(stack):
      out = io.BytesIO()
      while True:
        try:
          out.write(stack.popleft())
        except:
          break
      self.lines.append(out.getvalue())

    line = deque()
    while True:
      input = os.read(self.STDINFD,1024)
      if len(input) == 1 and input[0] in [3]:
        sys.exit(1)

      if len(input) == 1 and input[0] in [4]:
        add_line(line)
        break

      elif len(input) == 1 and input[0] in [127]: # backspace
        try:
            line.pop()
        except: pass

      elif len(input) == 1 and input[0] in [13]: # return
        add_line(line)

      else:
        line.append(input)

      self.terminal.send(input)

    termios.tcsetattr(self.STDINFD, termios.TCSANOW, self.saved_terminal_settings)


