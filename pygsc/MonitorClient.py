import socket
import time

class MonitorClient:
  def __init__(self,remote_hostname,local_hostname,port_range):
    self.remote_hostname = remote_hostname
    self.local_hostname = local_hostname
    self.port_range = port_range
    self.exit = False
    self.slots = []

  def add_slot(self,f):
    self.slots.append(f)

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
            ss.sendall( str(port).encode('utf-8') )

          # process messages from server
          connection,gsc_address = s.accept()
          while not self.exit:
            data = connection.recv(1024)
            for slot in self.slots:
              slot(data)
