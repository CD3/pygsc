import socket
import socketserver
import threading
import time
import logging
import json
import struct
logger = logging.getLogger(__name__)



class MonitorServer:

  def __init__(self, local_hostname, port):
    self.connections = []
    self.local_hostname = local_hostname
    self.port = port
    self.server = None
    self.listener_thread = None

  def listen_for_new_clients(self):
    ms = self
    class NewClientHandler(socketserver.BaseRequestHandler):
        def handle(self):
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect( (self.client_address[0], int(self.data)) )
            ms.connections.append(s)
            logger.info(f"Client connected: '{self.client_address}' on port '{self.data}'")

    logger.info(f"Setting up TCP server to listed for client connections on port {self.port} as {self.local_hostname}.")
    with socketserver.TCPServer((self.local_hostname, self.port), NewClientHandler) as server:
        self.server = server
        server.serve_forever()

  def broadcast_message(self,message):
    if not isinstance(message,(str,bytes)):
      message = json.dumps(message)

    if logger.isEnabledFor(logging.DEBUG):
      logger.debug(f"Broadcasting message: '{message}'")

    if not isinstance(message,bytes):
      message = message.encode('utf-8')

    message = struct.pack('>I',len(message)) + message

    live_connections = []
    for client in self.connections:
      try:
        client.sendall(message)
        if logger.isEnabledFor(logging.DEBUG):
          logger.debug(f"Actual message sent to {client}: '{message}'")
        live_connections.append(client)
      except BrokenPipeError:
        client.close()
      except ConnectionResetError:
        client.close()
    self.connections = live_connections


  def start(self):
    self.listener_thread = threading.Thread(target=self.listen_for_new_clients)
    self.listener_thread.start()

  def shutdown(self):
    if self.server:
      self.server.shutdown()
      self.server = None
    if self.listener_thread:
      self.listener_thread.join()
      self.listener_thread = None
