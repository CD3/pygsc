from pathlib import Path
import time

from .ScriptRecorder import *

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
def gsc(script,shell):

    shell = make_interactive_shell(shell)
    session = ScriptedSession(script,shell)
    session.run()



@click.command(help="Record gsc script.")
@click.argument("output",type=click.Path(exists=False))
@click.option("--shell","-s",help="The shell to use for running the script.")
def gsc_record(output,shell):
  output = pathlib.Path(output)

  shell = make_interactive_shell(shell)
  rec = ScriptRecorder(shell)
  rec.run()

  output.write_bytes(rec.get_bytes())
  print()
  print("Script recording finished.")

@click.command(help="Display keycodes for keypresses.")
def display_keycodes():
  import tty, termios, sys, os

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
