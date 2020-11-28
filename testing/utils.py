from pygsc import ucode
import tempfile

def tmpfile(lines):
  if isinstance(lines,str):
    lines = [lines]

  file = tempfile.NamedTemporaryFile(delete=False)
  file.write('\n'.join(lines).encode(ucode))
  file.close()

  return file.name

