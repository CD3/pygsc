import sys,os
import termios,tty
from collections import deque
import logging

logger = logging.getLogger(__name__)


class UserInputHandler:
  def __init__(self,inputfd):
    self.inputfd = inputfd
    self.chunk_size = 1024
    self.last_read_input = None
    self.filter_input = False

    self.saved_terminal_settings = termios.tcgetattr(self.inputfd)
    tty.setraw(self.inputfd)

    
    self.filters = []

  def clear_filters(self):
    self.filters = []

  def add_filter( self, f ):
    self.filters.append(f)

  def __del__(self):
    termios.tcsetattr(self.inputfd, termios.TCSANOW, self.saved_terminal_settings)

  def filter(self, input):
    if self.filter_input:
      for f in self.filters:
        input = f(input)

    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"filtered input to '{input}' ({len(input)} chars)")

    return input

  def read(self):
    self.last_read_input= os.read(self.inputfd,self.chunk_size)
    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"read '{self.last_read_input}' ({len(self.last_read_input)} chars)")

    return  self.filter(self.last_read_input)

  def get_ord(self):
    '''Return ordinal for last read input. If no ordinal exists, returns -1'''
    try:
      return ord(self.filter(self.last_read_input))
    except:
      return -1










