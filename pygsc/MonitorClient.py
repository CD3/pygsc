import socket
import select
import struct
import time
import logging
logger = logging.getLogger(__name__)

class MonitorClient:
  def __init__(self,remote_hostname,local_hostname,port_range):
    self.remote_hostname = remote_hostname
    self.local_hostname = local_hostname
    self.port_range = port_range
    self.exit = False
    self.slots = []

  def shutdown(self):
    self.exit = True

  def add_slot(self,f):
    self.slots.append(f)

  @staticmethod
  def recvn(fd,n):
    data = bytearray(n)
    i = 0
    while i < n:
      packet = fd.recv(n - i)
      if not packet:
        return None
      data[i:i+len(packet)] = packet
      i += len(packet)
    return data

  @staticmethod
  def recv_msg(fd):
    # read message length
    data = MonitorClient.recvn(fd,4)
    if not data or len(data) < 1:
      return None
    N = struct.unpack('>I', data)[0]
    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"Recieved message prefix: '{data}' indicates we need to read {N} bytes")
    # read message
    data = MonitorClient.recvn(fd,N)
    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"Recieved message body: '{data}'")

    if not data or len(data) < 1:
      return None

    return bytes(data)

  def start(self):
    # we need to:
    # 1. find a port we can listen on.
    # 2. bind a socket to the port.
    # 3. connect to server and send it the port we are listening on.
    # 4. wait for, and process, messages from server.
    for port in range(*self.port_range):
      # find open port
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
          s.bind( (self.local_hostname,port) )
        except:
          continue
        # we have a port with a socket attached.
        while not self.exit:

          # start listening for connections
          s.listen()
          # connect to server and send them our port.
          # we might have to wait.
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
            while ss.connect_ex( (self.remote_hostname,3000) ) != 0:
              time.sleep(1)
              if self.exit:
                return
            ss.sendall( str(port).encode('utf-8') )

          # process messages from server
          connection,gsc_address = s.accept()
          while not self.exit:
            ifds,ofds,efds = select.select([connection],[],[],1)
            if len(ifds) > 0:
              # read message length
              message = MonitorClient.recv_msg(connection)
              if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Recieved message: '{message}'")
              if message is None:
                break
              for slot in self.slots:
                slot(message)

          # s.shutdown(socket.SHUT_RDWR)
          if self.exit:
            return
