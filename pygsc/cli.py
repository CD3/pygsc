from pathlib import Path
import logging

from .ScriptRecorder import *
from .ScriptedSession import *

import click

def make_interactive_shell(shell):
    oshell = shell
    if shell is None:
        shell = os.environ.get("SHELL", "bash")

    shell = shell.split()
    shell[0] = shutil.which(shell[0])

    if shell[0] is None:
      raise click.RuntimeError("Could not find working shell for '{oshell}'. Check that it is in your path.")

    if Path(shell[0]).name in ['bash','zsh']:
      shell.append("-i")

    return shell


@click.command(help="Run a shell script interactivly.")
@click.argument("script",type=click.Path(exists=True))
@click.option("--shell","-s",help="The shell to use for running the script.")
@click.option("--debug","-d",is_flag=True,help="Log debug messages.")
@click.option("--verbose","-v",is_flag=True,help="Log info messages.")
def gsc(script,shell,debug,verbose):

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
    session = ScriptedSession(script,shell)
    try:
      session.run()
    finally:
      session.cleanup()
    logger.debug("Session finished")



@click.command(help="Record gsc script.")
@click.argument("output",type=click.Path(exists=False))
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
    print("utf-8:",f"`{input.decode('utf-8')}`",end="\n\r")
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
