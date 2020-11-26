from pygsc.UserInputHandler import UserInputHandler
import tempfile
import pytest
import os,sys

def test_user_input_handler_devel():
  handler = UserInputHandler(0)

  handler.queue_input("a")
  handler.queue_input("b")

  assert handler.read() == "a"
  assert handler.last_read == "a"
  assert handler.last_read_ord == ord("a")
  assert handler.read() == "b"

