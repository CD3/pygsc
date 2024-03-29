import pexpect
import pytest
import time
from utils import tmpfile


# NOTE: Only one character at a time should be sent to simulate key presses.
def print_output(proc):
  proc.expect(".")
  print(proc.before)
  print(proc.after)

@pytest.fixture
def simple_script():
  file = tmpfile(["echo hi"])
  return file

def test_SimpleScriptInsertMode(simple_script):

  child = pexpect.spawn(f"""gsc {simple_script} --shell bash --no-statusline --startup-command='PS1="$>>> "'""",timeout=2)
  # the prompt will be printed 3 times:
  # once when the setup command is echo'ed by the shell
  # once when the new prompt is printed by the shell
  # and one more time because the setup-command is loaded before the shell takes over
  child.expect(r"\$>>> ")
  child.expect(r"\$>>> ")
  child.expect(r"\$>>> ")

  assert child.send("b") == 1
  assert child.expect("e") == 0

  assert child.send("b") == 1
  assert child.expect("c") == 0

  assert child.send("b") == 1
  assert child.expect("h") == 0

  assert child.send("b") == 1
  assert child.expect("o") == 0

  assert child.send("b") == 1
  assert child.expect(" ") == 0

  assert child.send("b") == 1
  assert child.expect("h") == 0

  assert child.send("b") == 1
  assert child.expect("i") == 0

  assert child.send("b") == 1
  with pytest.raises(pexpect.exceptions.TIMEOUT):
    child.expect(".",timeout=1)

  child.sendcontrol(r"m") # send return
  assert child.expect("\r\n") == 0

  assert child.expect("hi\r\n") == 0

  child.expect(r"\$>>> ")

  child.sendcontrol(r"m")
  child.expect(pexpect.EOF)

  assert not child.isalive()

  child.close()
  # assert child.exitstatus == 0



def test_BackspaceInInsertMode(simple_script):

  child = pexpect.spawn(f"""./gsc {simple_script} --shell bash --no-statusline --startup-command='PS1="$>>> "'""",timeout=2)
  child.expect(r"\$>>> ")
  child.expect(r"\$>>> ")
  child.expect(r"\$>>> ")

  assert child.send("b") == 1
  assert child.expect("e") == 0

  assert child.send("b") == 1
  assert child.expect("c") == 0

  assert child.send(b'\x7f') == 1
  assert child.expect(b'\x08') == 0

  assert child.send("b") == 1
  assert child.expect("c") == 0

  assert child.send("b") == 1
  assert child.expect("h") == 0

  assert child.send("b") == 1
  assert child.expect("o") == 0

  assert child.send("b") == 1
  assert child.expect(" ") == 0

  assert child.send("b") == 1
  assert child.expect("h") == 0

  assert child.send("b") == 1
  assert child.expect("i") == 0

  assert child.send(b'\x7f') == 1
  assert child.expect(b'\x08') == 0

  assert child.send(b'\x7f') == 1
  assert child.expect(b'\x08') == 0

  assert child.send("b") == 1
  assert child.expect("h") == 0

  assert child.send("b") == 1
  assert child.expect("i") == 0


  child.terminate()

# def test_CommentsAreIgnored():

#   with open("script-3.sh", "w") as f:
#     f.write("# C: comment\n");
#     f.write("echo\n");

#   child = pexpect.spawn("""./gsc script-3.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")

#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.expect("echo") == 0



#   child.terminate()



#   with open("script-3.sh", "w") as f:
#     f.write("# C : comment 1\n");
#     f.write("#C: comment 2\n");
#     f.write(" # COMMENT : comment 3\n");
#     f.write(" #COMMENT: comment 3\n");
#     f.write("echo\n");

#   child = pexpect.spawn("""./gsc script-3.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")

#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.expect("echo") == 0



#   child.terminate()

# def test_CommandModeQuit():
#   with open("script-4.sh", "w") as f:
#     f.write("echo\n");

#   child = pexpect.spawn("""./gsc script-4.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   assert child.send("")
#   with pytest.raises(pexpect.exceptions.TIMEOUT):
#     child.expect(".",timeout=1)
#   assert child.send("b")
#   with pytest.raises(pexpect.exceptions.TIMEOUT):
#     child.expect(".",timeout=1)


#   assert child.isalive()

#   assert child.send("q")
#   time.sleep(1)

#   assert not child.isalive()

#   child.close()
#   assert child.exitstatus == 1

# def test_InsertModeQuit():
#   with open("script-5.sh", "w") as f:
#     f.write("echo\n");

#   child = pexpect.spawn("""./gsc script-5.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)

#   assert child.isalive()

#   child.send("")
#   time.sleep(1)

#   assert not child.isalive()

#   child.close()
#   assert child.exitstatus == 1

# def test_SilenceOutput():

#   with open("script-6.sh", "w") as f:
#     f.write("ls -l\n");
#     f.write("echo hi\n");

#   # this unit tests seems to fail a lot (but no consistently) if the 
#   child = pexpect.spawn("""./gsc script-6.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=10)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")

#   assert child.send("")
#   assert child.send("s")
#   assert child.send("i")

#   assert child.send("b")
#   assert child.send("b")

#   assert child.send("")
#   assert child.send("v")
#   assert child.send("i")

#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.expect(" -l") == 0

#   assert child.send("")
#   assert child.send("s")
#   assert child.send("i")

#   assert child.sendcontrol('m')
#   with pytest.raises(pexpect.exceptions.TIMEOUT):
#     child.expect(".",timeout=1)

#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send("b")
#   assert child.send(" ")
#   assert child.send("b")
#   assert child.send("b")
#   with pytest.raises(pexpect.exceptions.TIMEOUT):
#     child.expect(".",timeout=1)

#   # this seems to be flaky. sometimes the unit tests pass. sometimes they fail...
#   # assert child.send("")
#   # assert child.send("v")
#   # assert child.send("i")

#   # assert child.sendcontrol('m')
#   # assert child.expect("^\r\nhi") == 0

# def test_ForwardBackward():
#   with open("script-7.sh", "w") as f:
#     f.write("echo 1 \n");
#     f.write("echo 2 \n");
#     f.write("echo 3 \n");

#   child = pexpect.spawn("""./gsc script-7.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")

#   # skip first line
#   child.send("")
#   child.send("j")
#   child.send("i")

#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("echo 2") == 0

#   # go back to fist line
#   child.send("")
#   child.send("k")
#   child.send("k")
#   child.send("i")

#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("echo 1") == 0

#   # skip to end
#   child.send("")
#   child.send("j")
#   child.send("j")
#   child.send("j")
#   child.send("j")
#   child.send("j")
#   child.send("j")
#   child.send("j")
#   child.send("i")

#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("echo 3") == 0

#   # go back to begining
#   child.send("")
#   child.send("k")
#   child.send("k")
#   child.send("k")
#   child.send("i")

#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("echo 1") == 0

# def test_KeyBindings():
#   with open("script-8.sh", "w") as f:
#     f.write("echo 1 \n");
#     f.write("echo 2 \n");
#     f.write("echo 3 \n");

#   child = pexpect.spawn("""./gsc script-8.sh --shell bash --no-monitor --setup-command='PS1="$>>> "' --key-binding='120:CommandMode_Quit' """,timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")

#   assert child.send("")
#   with pytest.raises(pexpect.exceptions.TIMEOUT):
#     child.expect(".",timeout=1)

#   assert child.isalive()

#   assert child.send("x")
#   time.sleep(1)

#   assert not child.isalive()

# def test_ContextVariables():
#   with open("script-9.sh", "w") as f:
#     f.write("echo %msg% \n");

#   child = pexpect.spawn("""./gsc script-9.sh --shell bash --no-monitor --setup-command='PS1="$>>> "' --context-variable="'msg'='hello!'"' """,timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")

#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("echo ") == 0

#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("hello! ") == 0

# def test_ExitCommand():
#   with open("script-10.sh", "w") as f:
#     f.write("echo\n");
#     f.write("# EXIT\n");
#     f.write("echo\n");

#   child = pexpect.spawn("""./gsc script-10.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.isalive()
#   assert child.expect("echo") == 0

#   child.send("\r")
#   time.sleep(1)

#   assert not child.isalive()

#   child.close()
#   assert child.exitstatus == 0


# def test_SkipCommand():
#   with open("script-11.sh", "w") as f:
#     f.write("echo 1\n");
#     f.write("# SKIP\n");
#     f.write("echo 2\n");
#     f.write("# RESUME\n");
#     f.write("echo 3\n");

#   child = pexpect.spawn("""./gsc script-11.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("echo 1") == 0
#   child.sendcontrol(r"m")
#   assert child.expect("\r\n") == 0
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   child.send("b")
#   assert child.expect("echo 3") == 0


# def test_MultiCharInputIsIgnored():
#   with open("script-12.sh", "w") as f:
#     f.write("echo 1\n");

#   child = pexpect.spawn("""./gsc script-12.sh --shell bash --no-monitor --setup-command='PS1="$>>> "'""",timeout=2)
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")
#   child.expect(r"\$>>> ")

#   child.send("bb")
#   child.send("b")
#   child.expect("e") == 0
