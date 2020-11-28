import logging
logger = logging.getLogger(__name__)


try:
  from pyparsing import *
  have_pyparsing = True
except:
  logger.warning("pyparsing module could not be imported. Command parsing ability will be (severely) limited")
  have_pyparsing = False



class CommandParser:

  class Parsers:
    def __init__(self):
      self.command_name = None
      self.argument = QuotedString(quoteChar="'",unquoteResults=True) | QuotedString(quoteChar='"',unquoteResults=True) | Word(printables)

    @property
    def command_string(self):
      parser = Suppress(Literal("#")) + self.command_name("name") + Optional(Suppress(Literal(":"))) + ZeroOrMore(self.argument)('arguments')
      return parser

  def __init__(self):
    self.have_pyparsing = have_pyparsing
    self.parsers = self.Parsers()
    self.aliases = {}

  def add_command(self,name,aliases=[]):
    if self.parsers.command_name is None:
       self.parsers.command_name = Literal(name)
    else:
       self.parsers.command_name = self.parsers.command_name ^ Literal(name)

    for alias in aliases:
       self.parsers.command_name = self.parsers.command_name ^ Literal(alias)
       self.aliases[alias] = name



  def parse(self,text):
    try:
      result = self.parsers.command_string.parseString(text,parseAll=True)
      ret = {}
      ret["name"] = self.aliases.get(result.name,result.name)
      ret["args"] = result.arguments
      return ret
    except:
      return None



