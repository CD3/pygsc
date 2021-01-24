import os
from setuptools import setup, find_packages

__version__= '0.2'

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
  install_requires = ['click','blessings','urwid','pygame'],
  entry_points='''
  [console_scripts]
  gsc=pygsc.cli:gsc
  gsc-record=pygsc.cli:gsc_record
  gsc-display-keycodes=pygsc.cli:display_keycodes
  gsc-monitor=pygsc.cli:gsc_monitor
  gsc-monitor-test-client=pygsc.cli:gsc_monitor_test_client
  gsc-monitor-test-server=pygsc.cli:gsc_monitor_test_server
  ''',
)
