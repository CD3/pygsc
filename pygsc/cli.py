from pathlib import Path
import time

from .ScriptedSession import *

import click

@click.command(help="Run a shell script interactivly.")
@click.argument("script",type=click.Path(exists=True))
@click.option("--shell","-s",help="The shell to use for running the script.")
def gsc(script,shell):

  
    oshell = shell
    if shell is None:
        shell = os.environ.get("SHELL", "bash")

    shell = shell.split()
    shell[0] = shutil.which(shell[0])
    if shell[0] is None:
      raise click.BadOptionUsage("--shell/-s",f"ERROR: shell '{oshell}' does not appear to exist. Which returned '{shell[0]}'.")

    if Path(shell[0]).name in ['bash','zsh']:
      shell.append("-i")

    session = ScriptedSession(script,shell)
    session.run()



