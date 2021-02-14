
class CharTree:
  '''
  A class for storing character sequences that are easy to search.

  For example, if we wanted to know if a given text string started with
  one of the following character sequences:

  abcd
  abdd
  abde
  abde
  abff

  We could use the Python strings `find` method. However, this would require
  us to call find up to 5 times. If the text to be searched does not start with 'a',
  then we would not need to look any further.

  So a CharTree is a way of storing character sequences that makes it very easy to
  determine if a given sequence is *not* in the set.
  '''

  def __init__(self,prefix:str=""):
    self.prefix = prefix
    self.is_leaf = False
    self.chars = dict()

  def add_char(self,c):
    '''
    Add a character to this tree's children.

    If the child already exists, does nothing.
    '''
    if c not in self.chars:
      self.chars[c] = CharTree(self.prefix+c)

  def add_sequence(self,s:str) -> None:
    '''
    Add a sequence of characters to the tree.
    '''

    if type(s) is not str:
      raise "Currently, only adding character sequences with a string is supported"

    if len(s) == 0:
      self.is_leaf = True
      return

    self.add_char(s[0])
    self[s[0]].add_sequence(s[1:])





  def __getitem__(self,c):
    if len(c) < 1:
      return None

    if len(c) > 1:
      next = self[c[0]]
      if next is None:
        return next

      return self[c[0]][c[1:]]
    else:
      if c in self.chars:
        return self.chars[c]
      else:
        return None

  def __len__(self):
    return len(self.chars)

  def get_prefix(self):
    return self.prefix

  def get_string(self,c=None):
    if c is None:
      return self.get_prefix()
    return self.get_prefix() + c

  def match(self,text:str) -> str:
    '''
    Check if any character sequence in the tree matches text.
    '''
    if type(text) is not str:
      raise "Currently, only matching character sequencess against strings is supported."

    if len(text) < 1 or text[0] not in self.chars:
      if self.is_leaf:
        return self.get_string()
      else:
        return None

    # if we are here, then we know that the first char in text is match
    # check if the next char matches
    # if it does, return it
    # if it doesn't, return our text
    return self.chars[text[0]].match(text[1:])


    

    


    



