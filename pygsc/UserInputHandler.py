import sys,os
import termios,tty
from queue import Queue
import logging

logger = logging.getLogger(__name__)


class UserInputHandler:
  def __init__(self,inputfd):
    self.inputfd = inputfd
    self.chunk_size = 1024
    self.last_read_input = None
    self.filter_input = False
    self.filters = []
    self.queue = Queue()


  def clear_filters(self):
    self.filters = []

  def add_filter( self, f ):
    self.filters.append(f)


  def filter(self, input):
    if self.filter_input:
      for f in self.filters:
        input = f(input)

    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"filtered input to '{input}' ({len(input)} chars)")

    return input

  def queue_input(self,input):
    self.queue.put(input)

  def read(self):
    if self.queue.empty():
      self.last_read_input = os.read(self.inputfd,self.chunk_size)
    else:
      self.last_read_input = self.queue.get()

    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"read '{self.last_read_input}' ({len(self.last_read_input)} chars)")

    return  self.filter(self.last_read_input)

  @property
  def last_read(self):
    return self.filter(self.last_read_input)

  @property
  def last_read_ord(self):
    '''Return ordinal for last read input. If no ordinal exists, returns -1'''
    try:
      return ord(self.last_read)
    except:
      return -1










