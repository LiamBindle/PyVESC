from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
  name = 'pyvesc',
  packages = ['pyvesc'],
  version = '1.0.3',
  description = 'Python implementation of the VESC communication protocol.',
  author = 'Liam Bindle',
  author_email = 'liambindle@gmail.com',
  url = 'https://github.com/LiamBindle/PyVESC',
  download_url = 'https://github.com/LiamBindle/PyVESC/tarball/1.0.3',
  keywords = ['vesc', 'VESC', 'communication', 'protcol', 'packet'],
  classifiers = [],
  install_requires=required
)
