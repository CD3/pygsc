from .Script import *
from .TerminalSession import *
from .UserInputHandler import *
from .CommandParser import *
from .MonitorServer import *
from .MessageDisplay import *
from . import ucode
import sys,tty,string
import enum
import logging
try:
  import blessed
  have_blessed = True
except:
  have_blessed = False
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

        Returns True if session to continue to next line.
        '''
        cl = self.session.script.current_line()
        if cl is None:
          return False
        res = self.session.command_parser.parse(cl)
        if res is None:
          return False

        if res['name'] == "comment":
          self.session.script.seek_next_line()
          return False



        if res['name'] == "passthrough":
          self.session.mode = self.session.Modes.Passthrough
          self.session.script.seek_next_line()
          logger.debug(f"switching modes: insert -> pass-through")
          return True

        if res['name'] == "temporary passthrough":
            logger.debug(f"temporarily switching to pass-through mode")
            self.session.mode = self.session.Modes.TemporaryPassthrough
            self.session.script.seek_next_line()
            self.session.mode_handlers[self.session.mode].run()
            self.session.mode = self.session.Modes.Insert

        if res['name'] == "statusline":
          if len(res['args']) < 1:
            self.session.set_statusline(True)
          else:
            if res['args'][0].lower() in ["off","false","0","disable"]:
              self.session.set_statusline(False)
            elif res['args'][0].lower() in ["on","true","1","enable"]:
              self.session.set_statusline(True)
            else:
              logger.error(f"Unrecognized value '{res['args'][0]}' in statusline command. Ignoring.")
          self.session.script.seek_next_line()

        if res['name'] == "display":
          if self.session.message_display is None:
            if MessageDisplay is None:
              logger.error(f"Script contained a 'display' command, but no message displayer could be found. Make sure you have one of the supported GUI kits installed (pygame for example).")
              self.session.message_display = DummyMessageDisplay()
            else:
              self.session.message_display = MessageDisplay()

          if not self.session.message_display.is_running():
            self.session.message_display.start()

          if len(res['args']) > 0:
            self.session.message_display.set_message(res['args'][0])
          self.session.script.seek_next_line()

          return True
        
        if res['name'] == "pause":
          self.session.script.seek_next_line()
          if len(res['args']) > 0:
            t = float(res['args'][0])
            logger.info(f"Pausing for {t} seconds...")
            stime = time.perf_counter()
            while time.perf_counter() - stime < abs(t):
              input = self.session.input_handler.read(0.1)
              if input is not None:
                if t < 0:
                  break
                else:
                  if ord(input) in [4]:
                    break





          return True


        return False


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
        elif self.session.input_handler.last_read_ord in [16]: # ctl-p
          logger.debug(f"switching modes: insert -> passthrough")
          self.session.mode = self.session.Modes.Passthrough
          return True
        else:
          key = self.session.script.current_key()
          self.session.terminal.send(key)
          self.session.script.seek_next_col(len(key))

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
          if input in ["R"]:
            self.session.script.reload()

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
          elif self.session.input_handler.last_read_ord in [16]: # ctl-p
            logger.debug(f"switching modes: pass-through -> insert")
            self.session.mode = self.session.Modes.Insert
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
        self.command_parser = CommandParser()

        self.command_parser.add_command("passthrough", ['pass-through','pass'])
        self.command_parser.add_command("temporary passthrough",['temporary pass-through', 'temp pass'])
        self.command_parser.add_command("line")
        self.command_parser.add_command("mode")
        self.command_parser.add_command("statusline")
        self.command_parser.add_command("stdout")
        self.command_parser.add_command("pause")
        self.command_parser.add_command("comment")
        self.command_parser.add_command("display")

        if have_blessed:
          self.bterm = blessed.Terminal()
          self.detected_term_escape_sequences = list(blessed.keyboard.get_keyboard_sequences(self.bterm).keys())
        else:
          self.detected_term_escape_sequences = []
          if have_blessings:
            self.bterm = blessings.Terminal()
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


        self.monitor_server = None
        self.monitor_server_flag = False
        self.monitor_server_hostname = "localhost"
        self.monitor_server_port = 3000

        self.message_display = None

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

      if self.message_display is not None and self.message_display.is_running():
        self.message_display.shutdown()
      self.message_display = None


    def send_to_terminal(self,text):
      self.terminal.send(text)

    def disable_terminal_output(self):
      self.terminal.set_output_mode(self.terminal.OutputMode.Drop)

    def enable_terminal_output(self):
      self.terminal.set_output_mode(self.terminal.OutputMode.Print)

    def set_terminal_output_mode(self,mode):
      self.terminal.set_output_mode(mode)


    def run(self):
      if self.monitor_server_flag:
        self.start_monitor_server()
      while not self.exit_flag:
        self.update_statusline()
        self.mode_handlers[self.mode].run()

      self.stop_monitor_server()
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

      if self.monitor_server:
        self.send_state_to_monitors()

      
    def set_monitor(self,flag):
      self.monitor_server_flag = flag

    def toggle_monitor(self):
      self.monitor_server_flag = not self.monitor_server_flag

    def start_monitor_server(self):
      self.monitor_server = MonitorServer(self.monitor_server_hostname,self.monitor_server_port)
      self.monitor_server.start()

    def stop_monitor_server(self):
      if self.monitor_server:
        self.monitor_server.shutdown()
        self.monitor_server = None

    def send_state_to_monitors(self):
      state = {'mode':str(self.mode),
          'pos': (self.script.line,  self.script.col),
          'lines': self.script.lines
          }
      self.monitor_server.broadcast_message(state)


    def set_message_display(self,display):
      self.message_display = display




