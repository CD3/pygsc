from .Script import *
from .TerminalSession import *
from .UserInputHandler import *
import sys,tty,string
import enum
import logging

logger = logging.getLogger(__name__)

class ScriptedSession:
    


    class Mode:
      def __init__(self,session):
        self.session = session

    class InsertMode(Mode):
      def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

      def run(self):
        logger.debug("entering insert mode")
        while not self.session.script.eof():
          while not self.session.script.eol():
            if self.handle_script_current_char(): return
          if self.handle_script_eol(): return
        if self.handle_script_eof(): return

        self.session.exit_flag = True

      def handle_script_current_char(self):
        '''
        Read input from user and decide what to
        do with the current script character.
        '''
        input = self.session.input_handler.read()
        if self.session.input_handler.last_read_ord in [127]: # backspace
          self.session.terminal.send(chr(127))
          self.session.script.seek_prev_col()
        elif self.session.input_handler.last_read_ord in [4]: # ctl-d
          logger.debug(f"switching modes: insert -> command")
          self.session.mode = self.session.Modes.Command
          return True
        else:
          self.session.terminal.send(self.session.script.current_char())
          self.session.script.seek_next_col()

        return False

        
      def handle_script_eol(self):
        '''
        Read input from user and decide what to
        do at the end of the line.
        '''
        while True:
          input = self.session.input_handler.read().decode('utf-8')
          if self.session.input_handler.last_read_ord in [127]: # backspace
            self.session.terminal.send(chr(127))
            self.session.script.seek_prev_col()
            return False

          if self.session.input_handler.last_read_ord in [4]: # ctl-d
            logger.debug(f"switching modes: insert -> command")
            self.session.mode = self.session.Modes.Command
            return True

          if self.session.input_handler.last_read_ord in [13]: # return
            self.session.terminal.send('\r')
            self.session.script.seek_next_line()
            return False



      def handle_script_eof(self):
        '''
        Read input from user and decide what to
        do at the end of the file.
        '''
        while True:
          input = self.session.input_handler.read().decode('utf-8')
          if self.session.input_handler.last_read_ord in [13]: # return
            logger.debug(f"recieved user input {input}. exitting")
            return False
          elif self.session.input_handler.last_read_ord in [4]: # ctl-4
            logger.debug(f"switching modes: insert -> command")
            self.session.mode = self.session.Modes.Command
            return True
          else:
            logger.debug(f"recieved user input {input} (ord {self.session.input_handler.last_read_ord}), but did not exit")





    class CommandMode(Mode):
      def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

      def run(self):
        logger.debug("entering command mode")
        self.handle_user_input()
        logger.debug("exiting command mode")

      def handle_user_input(self):
        while True:
          input = self.session.input_handler.read().decode('utf-8')
          if input in ["i"]:
            logger.debug(f"switching modes: command -> insert")
            self.session.mode = self.session.Modes.Insert
            return
          if input in ["p"]:
            logger.debug(f"switching to passthrough mode")
            self.session.mode = self.session.Modes.Passthrough
            return
          if input in ["h"]:
            self.session.script.seek_prev_col()
          if input in ["j"]:
            self.session.script.seek_next_line(ret=False)
          if input in ["k"]:
            self.session.script.seek_prev_line(ret=False)
          if input in ["l"]:
            self.session.script.seek_next_col()
          if input in ["^"]:
            self.session.script.seek_beg_col()
          if input in ["$"]:
            self.session.script.seek_end_col()


    class PassthroughMode(Mode):
      def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

      def run(self):
        logger.debug("passthrough mode running")
        while True:
          input = self.session.input_handler.read().decode('utf-8')
          if self.session.input_handler.last_read_ord in [4]: # ctl-d
            logger.debug("switching mode: passthruogh -> command")
            self.session.mode = self.session.Modes.Command
            return
          self.session.terminal.send(input)


    Modes = Enum("Modes",'Insert Command Passthrough')
    def __init__(self, script, shell):
        self.script = Script(script)
        self.shell = shell
        self.STDINFD = sys.stdin.fileno()
        self.exit_flag = False
        self.terminal = TerminalSession(self.shell)
        self.saved_terminal_settings = None

        try:
          self.saved_terminal_settings = termios.tcgetattr(self.STDINFD)
          tty.setraw(self.STDINFD)
        except:
          logging.warning("Could not save terminal state for stdin. This likely means that no terminal is in control.")

        self.input_handler = UserInputHandler(self.STDINFD)

        self.mode = self.Modes.Insert
        self.mode_handlers = {self.Modes.Insert:self.InsertMode(self),self.Modes.Command:self.CommandMode(self),self.Modes.Passthrough:self.PassthroughMode(self)}

    def cleanup(self):
      try:
        logger.debug("trying to stop terminal session")
        self.terminal.stop()
      except Exception as e:
        logger.debug(f"there was en error: {e}")

      if self.saved_terminal_settings is not None:
        try:
          logger.debug("trying to restore terminal settings")
          termios.tcsetattr(self.STDINFD, termios.TCSANOW, self.saved_terminal_settings)
        except Exception as e:
          logger.debug(f"there was en error: {e}")



    def run(self):
      while not self.exit_flag:
        self.mode_handlers[self.mode].run()

      logger.debug("Exiting session")








