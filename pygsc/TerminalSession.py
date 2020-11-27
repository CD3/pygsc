import tty
import pty
import os
import sys
import select
import termios
import threading
import time
import pathlib
import shutil
import signal
import fcntl
import struct
from queue import Queue
from enum import Enum
from . import ucode



class TerminalSession:
  class OutputMode(Enum):
    Print = 1
    Pause = 2
    Drop = 3


  def __init__(self,shell:list):

    self.output_mode = TerminalSession.OutputMode.Print
    self.STDINFD = sys.stdin.fileno()
    self.STDOUTFD = sys.stdout.fileno()
    self.STDERRFD = sys.stderr.fileno()
    self.shutdown_flag = False

    self.slavePID,self.termfd = pty.fork()

    if self.slavePID == pty.CHILD:
      os.execvp(shell[0], shell)

    # child proc will not make it to this point
    self.sync_windows_size()

    self.terminal_output_thread = threading.Thread(target=self._process_terminal_output)
    self.terminal_output_thread.start()

    self.output_callbacks = []


  def add_output_callback(self,f):
    self.output_callbacks.append(f)


  def _process_terminal_output(self):
    poll = select.poll()
    poll.register(self.termfd,select.POLLIN)

    stash = Queue()

    while not self.shutdown_flag:
      res = poll.poll(100)
      for fd,evm in res:
        if evm & select.POLLIN:
          c = os.read(fd,1024)
          if self.output_mode == TerminalSession.OutputMode.Drop:
            continue

          if self.output_mode == TerminalSession.OutputMode.Print:
            while not stash.empty():
              os.write(self.STDOUTFD,stash.get())
            os.write(self.STDOUTFD,c)

          if self.output_mode == TerminalSession.OutputMode.Pause:
            stash.put(c)

          for f in self.output_callbacks:
            f(c)
            

  def stop(self):
    os.kill(self.slavePID, signal.SIGKILL)
    self.shutdown_flag = True
    self.terminal_output_thread.join()


  def send(self,c : str):
    if not isinstance(c,bytes):
      c = c.encode(ucode)
    os.write(self.termfd,c)

  def sync_windows_size(self):
    winsz = struct.pack('HHHH',0,0,0,0)
    winsz = fcntl.ioctl(self.STDINFD, termios.TIOCGWINSZ, winsz)
    fcntl.ioctl(self.termfd, termios.TIOCSWINSZ, winsz)


  
  def set_output_mode(self,mode : OutputMode):
    self.output_mode = mode


