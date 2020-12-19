import sys,os
import select
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
    self.callbacks = []
    self.queue = Queue()


  def clear_filters(self):
    self.filters = []

  def add_filter( self, f ):
    self.filters.append(f)

  def add_callback( self, c ):
    self.callbacks.append(c)


  def filter(self, input):
    if self.filter_input:
      for f in self.filters:
        input = f(input)

    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"filtered input to '{input}' ({len(input)} chars)")

    return input

  def run_callbacks(self):
    for c in self.callbacks:
      c()

  def queue_input(self,input):
    self.queue.put(input)

  def read(self,timeout=None):
    if self.queue.empty():
      if timeout is None:
        self.last_read_input = os.read(self.inputfd,self.chunk_size)
      else:
        r,w,e = select.select([self.inputfd], [], [], timeout)
        if self.inputfd in r:
          self.last_read_input = os.read(self.inputfd,self.chunk_size)
        else:
          self.last_read_input = None
    else:
      self.last_read_input = self.queue.get()

    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"read '{self.last_read_input}' ({len(self.last_read_input)} chars)")

    self.run_callbacks()

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










