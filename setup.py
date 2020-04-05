from setuptools import setup

VERSION = '1.0.5'

setup(
  name='pyvesc',
  packages=['pyvesc', 'pyvesc.protocol', 'pyvesc.protocol.packet', 'pyvesc.VESC', 'pyvesc.VESC.messages'],
  version=VERSION,
  description='Python implementation of the VESC communication protocol.',
  author='Liam Bindle',
  author_email='liambindle@gmail.com',
  url='https://github.com/LiamBindle/PyVESC',
  download_url='https://github.com/LiamBindle/PyVESC/tarball/' + VERSION,
  keywords=['vesc', 'VESC', 'communication', 'protocol', 'packet'],
  classifiers=[],
  install_requires=['crccheck']
)
