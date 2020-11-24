import os
from setuptools import setup, find_packages

__version__= '0.1'

setup(
  name = 'pygsc',
  packages = ['pygsc'],
  version = __version__,
  description = "Run command line demos from a script.",
  license='MIT',
  author = 'CD Clark III',
  author_email = 'clifton.clark@gmail.com',
  url = 'https://github.com/CD3/pygsc',
  download_url = f'https://github.com/CD3/pygsc/archive/{__version__}.tar.gz',
  install_requires = ['click','prompt_toolkit'],
  entry_points='''
  [console_scripts]
  pygsc=pygsc.cli:gsc
  ''',
)
