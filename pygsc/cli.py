from pathlib import Path
import logging
import threading
import time
import json
import os,sys
import select
import socket


from .ScriptRecorder import *
from .ScriptedSession import *
from .MonitorServer import *
from .MonitorClient import *
from . import ucode

import click

def make_interactive_shell(shell):
    oshell = shell
    if shell is None:
        shell = os.environ.get("SHELL", "bash")

    shell = shell.split()
    shell[0] = shutil.which(shell[0])

    if shell[0] is None:
      raise click.RuntimeError("Could not find working shell for '{oshell}'. Check that it is in your path.")

    return shell

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@click.command(help="Run a shell script interactivly.")
@click.argument("script",type=click.Path(exists=True))
@click.version_option()
@click.option("--shell","-s",help="The shell to use for running the script.")
@click.option("--debug","-d",is_flag=True,help="Log debug messages.")
@click.option("--verbose","-v",is_flag=True,help="Log info messages.")
@click.option("--no-statusline/--statusline",help="disable/enable status line (the statusline may interfere with some full screen applications, such as vim). status line is enabled by default.")
@click.option("--line-mode","-l",is_flag=True,help="Start script in line mode.")
@click.option("--startup-command", multiple=True, help="Send TEXT to the terminal before starting input (a \\r will be appended). May be given multiple times.")
@click.option("--monitor/--no-monitor",  help="Run a server to send status information to gsc monitor clients (such as gsc-monitor).")
@click.option("--monitor-hostname", default="auto", help="Specify the hostname to use for the gsc monitor server (default auto).")
@click.option("--no-render", is_flag=True, help="Do not perform variable expansion in the script file before running. Variables in the script are identified with %{VarName} (so that they do not interfere with shell variables ${VarName} that may be used in the script). By default, environment variables will be expanded.")
@click.option("--multi-char-keys", default='auto', help="Specify a list of multi-character keypresses that should be detected in scripts and send as single input to the terminal. Currently only supports 'auto', which will use the `blessed` module to add all key press escape sequences listed in terminfo.")
def gsc(script,shell,debug,verbose,no_statusline,line_mode,startup_command,monitor,monitor_hostname,no_render,multi_char_keys):

    logger = None
    if verbose or debug:
      logger = logging.getLogger()
      fh = logging.FileHandler("gsc.log")
      fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
      fh.setFormatter(fmt)
      logger.addHandler(fh)
      if verbose:
        logger.setLevel(logging.INFO)
      if debug:
        logger.setLevel(logging.DEBUG)

    shell = make_interactive_shell(shell)
    if logger:
      logger.debug(f"Shell: {shell}")
    session = ScriptedSession(script,shell)
    if not no_render:
      session.script.render(os.environ)

    
    if multi_char_keys == "auto":
      if len(session.detected_term_escape_sequences) > 1:
        for k in session.detected_term_escape_sequences:
          session.script.add_multi_char_key(k)
      else:
        # if we didn't detect any sequences, add some common ones
        # that should be defined for all xterm-compatible terminals
        session.script.add_multi_char_key('OD')  # left arrow
        session.script.add_multi_char_key('OC')  # right arrow
        session.script.add_multi_char_key('OB')  # down arrow
        session.script.add_multi_char_key('OA')  # up arrow
        session.script.add_multi_char_key('[3~') # delete



    session.set_statusline(not no_statusline)
    if monitor:
      session.monitor_server_hostname = get_my_ip() if monitor_hostname == "auto" else monitor_hostname
      session.set_monitor(monitor)

    if line_mode:
      session.mode = session.Modes.Line
    try:
      for command in startup_command:
        session.send_to_terminal(command+"\r")
      session.run()
    finally:
      session.cleanup()

    if logger:
      logger.debug("Session finished")

    if session.script.line == len(session.script.lines) - 1:
      return sys.exit(0)
    else:
      return sys.exit(1)



@click.command(help="Record gsc script.")
@click.argument("output",type=click.Path(exists=False))
@click.version_option()
@click.option("--shell","-s",help="The shell to use for running the script.")
def gsc_record(output,shell):
  output = pathlib.Path(output)

  shell = make_interactive_shell(shell)
  rec = ScriptRecorder(shell)
  rec.run()
  rec.cleanup()

  output.write_bytes(rec.get_bytes())
  print()
  print("Script recording finished.")



@click.command(help="Display keycodes for keypresses.")
@click.version_option()
@click.option("--keypress-driver","-k",is_flag=True,help="Use keypress event driver instead of characters from stdin.")
def display_keycodes(keypress_driver):
  import tty, termios, sys, os
  import collections

  try:
    from pynput.keyboard import Key,KeyCode,Listener
    have_pynput = True
  except:
    have_pynput = False

  
  if keypress_driver:
    if not have_pynput:
      print("Could not run keypress-based driver. `pynput` is not installed.")
      sys.exit(1)

    def on_press(key):
      print("stroke: down")
      print("raw:",key)
      print("type:",type(key))
      if type(key) == KeyCode:
        print("dead:",key.is_dead)
        print("char:",key.char)
      else:
        print("val:",key.value)
      print()

    def on_release(key):
      print("stroke: up")
      print("raw:",key)
      print("type:",type(key))
      if type(key) == KeyCode:
        print("dead:",key.is_dead)
        print("char:",key.char)
      else:
        print("val:",key.value)
      print()

      if key == Key.esc:
        return False

    with Listener(on_press=on_press,on_release=on_release) as listener:
      listener.join()

    return



  saved = termios.tcgetattr(sys.stdin.fileno())
  tty.setraw(sys.stdin.fileno())
  while True:
    input = os.read(sys.stdin.fileno(),1024)
    print(len(input),'chars',end='\n\r')
    print("raw:",f"`{input}`",end="\n\r")
    print("unicod:",f"`{input.decode(ucode)}`",end="\n\r")
    sys.stdout.write("int: ")
    for c in input:
      sys.stdout.write(f"{c} ")
    print(end="\n\r")
    sys.stdout.write("hex: ")
    for c in input:
      sys.stdout.write(f"{hex(c)} ")
    print(end="\n\r")
    print(end="\n\r")

    if len(input) == 1 and ord(input) == 4:
      break


  termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,saved)


@click.command(help="A gsc monitor client to status information about the current gsc session.")
@click.version_option()
@click.option("--remote-hostname","-r",default='localhost',help="The remote server (running gsc) hostname.")
@click.option("--local-hostname","-l",default='auto',help="The local server (running gsc-monitor) hostname.")
@click.option("--port","-p",help="Specify the (local) port to use for communicating with gsc session.")
@click.option("--debug","-d",is_flag=True,help="Log debug messages.")
@click.option("--verbose","-v",is_flag=True,help="Log info messages.")
def gsc_monitor(remote_hostname,local_hostname,port,debug,verbose):
  logger = None
  if verbose or debug:
    logger = logging.getLogger()
    fh = logging.FileHandler("gsc-monitor.log")
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    if verbose:
      logger.setLevel(logging.INFO)
    if debug:
      logger.setLevel(logging.DEBUG)

  port_range = (3001,3020)
  if port:
    port_range = (port,port)



  try:
    import urwid
  except:
    print("ERROR: could not import 'urwid' module. Please install it and try again.")
    sys.exit(1)


  piper,pipew = os.pipe()
  if local_hostname == 'auto':
    local_hostname = get_my_ip()
  gsc_monitor = MonitorClient(remote_hostname,local_hostname,port_range)
  gsc_monitor.add_slot(lambda data: os.write(pipew,data))



  def handle_input(char):
    if char in ('q','Q'):
      raise urwid.ExitMainLoop()

  def message_handler():
    message = os.read(piper,8096)
    try:
      state = json.loads(message.decode('utf-8'))
    except:
      if logger:
        logger.error(f"Could not decode message: {message}")
      return
    l,c = state['pos']
    completed_lines = '\n'.join(state['lines'][0:l])+'\n'
    current_line_completed_chars = state['lines'][l][:c]
    current_line_upcomming_chars = state['lines'][l][c:]+'\n'
    upcomming_lines = '\n'.join(state['lines'][l+1:])+'\n'
    text = []
    text.append( ('dg',completed_lines) )
    text.append( ('dr',current_line_completed_chars) )
    text.append( ('lr',current_line_upcomming_chars) )
    text.append( ('lg',upcomming_lines) )
    body.set_text(text)


  # print(urwid.get_all_fonts())
  body = urwid.Text("")
  main_frame = urwid.Frame(body=urwid.Filler(body), header=urwid.Text("gsc Monitor"))


  palette = [
      ('divider','','','','g27','#a06'),
      ('lg','light gray','default'),
      ('dg','dark gray','default'),
      ('dr','dark red','default'),
      ('lr','light red','default'),
      ]
  loop = urwid.MainLoop(main_frame,palette=palette,unhandled_input=handle_input)
  loop.watch_file(piper,message_handler)
  # loop.set_alarm_in(0.1,poll,None)
  
  client_thread = threading.Thread(target=gsc_monitor.start)
  client_thread.start()
  loop.run()
  gsc_monitor.shutdown()
  client_thread.join()





@click.command(help="A gsc monitor test client to test gsc monitor servers.")
@click.version_option()
@click.option("--remote-hostname","-r",default='localhost',help="The remote server (running gsc) hostname.")
@click.option("--local-hostname","-l",default='auto',help="The local server (running gsc-monitor) hostname.")
@click.option("--port","-p",help="Specify the (local) port to use for communicating with gsc session.")
def gsc_monitor_test_client(remote_hostname,local_hostname,port):
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  ch = logging.StreamHandler()
  logger.addHandler(ch)

  if local_hostname == 'auto':
    local_hostname = get_my_ip()


  port_range = (3001,3020)
  if port:
    port_range = (port,port)


  gsc_monitor = MonitorClient(remote_hostname,local_hostname,port_range)
  gsc_monitor.add_slot(lambda data: print(f"Recieved: '{data}'"))
  thread = threading.Thread(target=gsc_monitor.start)
  thread.start()
  print("Press enter to shutdown:")
  exit = False
  while not exit:
    ready = select.select([sys.stdin],[],[],1)[0]
    if ready:
      exit = True
  gsc_monitor.shutdown()
  thread.join()




@click.command(help="Run a gsc monitor server to test gsc monitor clients.")
@click.version_option()
@click.option("--local-hostname","-l",default="auto",help="The server hostname.")
@click.option("--port","-p",default=3000,help="Specify the (local) port to lisiten for new clients on.")
def gsc_monitor_test_server(local_hostname,port):
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  ch = logging.StreamHandler()
  logger.addHandler(ch)

  if local_hostname == 'auto':
    local_hostname = get_my_ip()
  server = MonitorServer(local_hostname,port)
  server.start()
  print("Press enter to shutdown:")
  exit = False
  while not exit:
    ready = select.select([sys.stdin],[],[],1)[0]
    if ready:
      exit = True
    else:
      mesg = {'desc' : 'test message', 'mode' : 'Modes.Insert', 'lines' : ["pwd","ls","cat tmp.txt","gnuplot","exit"], 'pos':(2,5)}
      server.broadcast_message(mesg)

  server.shutdown()
