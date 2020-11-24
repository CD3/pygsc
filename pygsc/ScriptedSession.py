from .Script import *
from .TerminalSession import *
import sys,tty,string

class ScriptedSession:
    def __init__(self, script, shell):
        self.script = Script(script)
        self.shell = shell
        self.STDINFD = sys.stdin.fileno()
        self.exit_flag = False
        self.terminal = TerminalSession(self.shell)

    def __del__(self):
      self.terminal.stop()


    def run(self):
        saved_terminal_settings = termios.tcgetattr(self.STDINFD)
        tty.setraw(self.STDINFD)


        while not self.script.eof():
          # process line for instructions
          while not self.script.eol():
            self.handle_script_current_char()
          self.handle_script_eol()
        self.handle_script_eof()


        termios.tcsetattr(self.STDINFD, termios.TCSANOW, saved_terminal_settings)


    def handle_script_current_char(self):
      '''
      Read input from user and decide what to
      do with the current script character.
      '''
      c = os.read(self.STDINFD,1024)
      if len(c) == 1 and ord(c) in [127]: # backspace
        # send backspace to terminal and backup script char
        self.terminal.send(chr(127))
        self.script.seek_prev_char()
      else:
        self.terminal.send(self.script.current_char())
        self.script.seek_next_char()

      
    def handle_script_eol(self):
      '''
      Read input from user and decide what to
      do at the end of the line.
      '''
      while True:
        c = os.read(self.STDINFD,1024)
        if len(c) == 1 and ord(c) in [127]: # backspace
          self.terminal.send(chr(127))
          self.script.seek_prev_char()
          return

        if len(c) == 1 and ord(c) in [13]: # return
          self.terminal.send('\r')
          self.script.seek_next_line()
          return


    def handle_script_eof(self):
      '''
      Read input from user and decide what to
      do at the end of the file.
      '''
      while True:
        c = os.read(self.STDINFD,1024)
        if len(c) == 1 and ord(c) in [13]: # return
          return


