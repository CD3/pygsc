from .Script import *
from .TerminalSession import *
from .UserInputHandler import *
from . import ucode
import sys,tty,string
import enum
import logging
try:
  import blessings
  have_blessings = True
except:
  have_blessings = False

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
          if self.handle_script_line(): return
          while not self.session.script.eol():
            if self.handle_script_current_char(): return
            self.session.update_statusline()
          if self.handle_script_eol(): return
          self.session.update_statusline()
        if self.handle_script_eof(): return
        self.session.update_statusline()

        self.session.exit_flag = True

      def handle_script_line(self):
        '''
        Look at current script line and
        take any actions necessary.
        '''
        cl = self.session.script.current_line()
        if cl is None:
          return False

        if not cl.strip().startswith('#'):
          return False

        cl = cl.strip()[1:].strip()

        if cl.lower() == "pass-through":
          self.session.mode = self.session.Modes.Passthrough
          self.session.script.seek_next_line()
          logger.debug(f"switching modes: insert -> pass-through")
          return True

        if cl.lower() == "command":
          self.session.mode = self.session.Modes.Command
          self.session.script.seek_next_line()
          logger.debug(f"switching modes: insert -> command")
          return True

        if cl.lower() == "temporary pass-through":
            logger.debug(f"temporarily switching to pass-through mode")
            self.session.mode = self.session.Modes.TemporaryPassthrough
            self.session.script.seek_next_line()
            self.session.mode_handlers[self.session.mode].run()
            self.session.mode = self.session.Modes.Insert

        if cl.startswith("statusline:"):
          toks = cl.split()
          if toks[-1] == "off":
            self.session.set_statusline(False)
          else:
            self.session.set_statusline(True)
          self.session.script.seek_next_line()

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
        elif self.session.input_handler.last_read_ord in [3]: # ctl-c
          self.session.exit_flag = True
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
          input = self.session.input_handler.read().decode(ucode)
          if self.session.input_handler.last_read_ord in [127]: # backspace
            self.session.terminal.send(chr(127))
            self.session.script.seek_prev_col()
            return False

          if self.session.input_handler.last_read_ord in [4]: # ctl-d
            logger.debug(f"switching modes: insert -> command")
            self.session.mode = self.session.Modes.Command
            return True

          if self.session.input_handler.last_read_ord in [3]: # ctl-c
            self.session.exit_flag = True
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
          input = self.session.input_handler.read().decode(ucode)
          if self.session.input_handler.last_read_ord in [13]: # return
            logger.debug(f"recieved user input {input}. exitting")
            return False
          elif self.session.input_handler.last_read_ord in [4]: # ctl-4
            logger.debug(f"switching modes: insert -> command")
            self.session.mode = self.session.Modes.Command
            return True
          else:
            logger.debug(f"recieved user input {input} (ord {self.session.input_handler.last_read_ord}), but did not exit")


    class LineMode(InsertMode):
      def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

      def handle_script_current_char(self):
        '''
        Overload InserMode single char handler to send entire lines.
        '''
        line = self.session.script.current_line()
        self.session.script.seek_end_col()
        self.session.terminal.send(line)
        return False





    class CommandMode(Mode):
      def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

      def run(self):
        logger.debug("entering command mode")
        self.handle_user_input()
        logger.debug("exiting command mode")

      def handle_user_input(self):
        while True:
          input = self.session.input_handler.read().decode(ucode)
          if input in ["i"]:
            logger.debug(f"switching modes: command -> insert")
            self.session.mode = self.session.Modes.Insert
            return
          if input in ["I"]:
            logger.debug(f"switching modes: command -> line")
            self.session.mode = self.session.Modes.Line
            return
          if input in ["p"]:
            logger.debug(f"switching to pass-through mode")
            self.session.mode = self.session.Modes.Passthrough
            return
          if input in ["P"]:
            logger.debug(f"temporarily switching to pass-through mode")
            self.session.mode = self.session.Modes.TemporaryPassthrough
            self.session.mode_handlers[self.session.mode].run()
            self.session.mode = self.session.Modes.Command
          if input in ["q"]:
            self.session.exit_flag = True
            return
          if input in ["s"]:
            self.session.toggle_statusline()
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

          self.session.update_statusline()


    class PassthroughMode(Mode):
      def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

      def run(self):
        logger.debug("entering pass-through mode")
        self.session.update_statusline()
        while True:
          input = self.session.input_handler.read().decode(ucode)
          if self.session.input_handler.last_read_ord in [4]: # ctl-d
            logger.debug("switching mode: pass-through -> command")
            self.session.mode = self.session.Modes.Command
            return
          self.session.terminal.send(input)
          self.session.update_statusline()


    class TemporaryPassthroughMode(Mode):
      def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

      def run(self):
        logger.debug("entering temporary pass-through mode")
        self.session.update_statusline()
        while True:
          input = self.session.input_handler.read().decode(ucode)
          self.session.terminal.send(input)
          self.session.update_statusline()
          if self.session.input_handler.last_read_ord in [13]: # return
            logger.debug("exiting temporary pass-through mode")
            return






    Modes = Enum("Modes",'Insert Line Command Passthrough TemporaryPassthrough')
    def __init__(self, script, shell):
        self.script = Script(script)
        self.shell = shell
        self.STDINFD = sys.stdin.fileno()
        self.exit_flag = False
        self.statusline_flag = False
        self.terminal = TerminalSession(self.shell)
        self.terminal.add_output_callback( lambda c: self.update_statusline() )
        self.saved_terminal_settings = None

        if have_blessings:
          self.bterm = blessings.Terminal()
          # print(self.bterm.clear())
        else:
          self.bterm = None

        try:
          self.saved_terminal_settings = termios.tcgetattr(self.STDINFD)
          tty.setraw(self.STDINFD)
        except:
          logging.warning("Could not save terminal state for stdin. This likely means that no terminal is in control.")

        self.input_handler = UserInputHandler(self.STDINFD)

        self.mode = self.Modes.Insert
        self.mode_handlers = {self.Modes.Insert:self.InsertMode(self),
                              self.Modes.Line:self.LineMode(self),
                              self.Modes.Command:self.CommandMode(self),
                              self.Modes.Passthrough:self.PassthroughMode(self),
                              self.Modes.TemporaryPassthrough:self.TemporaryPassthroughMode(self),
                              }
        self.mode_status_abbrvs = {self.Modes.Insert:"I",
                                   self.Modes.Command:"C",
                                   self.Modes.Passthrough:"P",
                                   self.Modes.TemporaryPassthrough:"T",
                                   self.Modes.Line:"L"}

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


    def send_to_terminal(self,text):
      self.terminal.send(text)

    def disable_terminal_output(self):
      self.terminal.set_output_mode(self.terminal.OutputMode.Drop)

    def enable_terminal_output(self):
      self.terminal.set_output_mode(self.terminal.OutputMode.Print)

    def set_terminal_output_mode(self,mode):
      self.terminal.set_output_mode(mode)


    def run(self):
      while not self.exit_flag:
        self.update_statusline()
        self.mode_handlers[self.mode].run()

      logger.debug("Exiting session")


    def set_statusline(self,flag):
      self.statusline_flag = flag
    def toggle_statusline(self):
      self.statusline_flag = not self.statusline_flag

    def update_statusline(self):
      if self.statusline_flag:
        mode = self.mode_status_abbrvs[self.mode]
        lno = self.script.line + 1
        lNo = len(self.script.lines)
        cno = self.script.col + 1
        cNo = len(self.script.current_line(""))

        sline = f" {mode} {lno:03}/{lNo:03} {cno:03}/{cNo:03}"

        if self.bterm is not None:
          t = self.bterm
          os.write( self.terminal.STDOUTFD, (t.save() + t.move(0,t.width-len(sline)) + sline + t.restore()).encode(ucode) )
      







