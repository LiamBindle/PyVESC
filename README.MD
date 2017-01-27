# PyVESC [![Build Status](https://travis-ci.org/LiamBindle/PyVESC.svg?branch=init-dev)](https://travis-ci.org/LiamBindle/PyVESC)
PyVESC is aimed at being a easy to use and robust python implementation of the
communication protocol used by the
[VESC - Open Source ESC](http://vedder.se/2015/01/vesc-open-source-esc/) by
Benjamin Vedder. Its a great project with a really great community and I'd urge
anyone interested in motor controllers to take a look at it.


This repository was developed for the [University of Saskatchewan Space Design
Team](https://usst.ca), as we are currently using these controllers for all of
our motor controller needs.

## Purpose
The primary aim of PyVESC allows VESC message objects to be encoded and decoded.
In addition to this PyVESC aims to be easily extensible to support custom
messages and well as robust in handling corrupt data packets.

This is accomplished by breaking the project up into two somewhat distinct
ideas:

1. A means for encoding (object to bytes) and decoding (bytes to object) objects
which represent messages. These objects should be easily extensible and easy to
declare. This is accomplished in the ```pyvesc.messages``` module.
2. A means for encoding (bytes to bytes) and decoding(bytes to bytes) arbitrary
data packets. Encoding and decoding must be robust and packets must be validated
so corrupted packets do not produce erroneous behavior. This is accomplished in
the ```pyvesc.packet``` module.

## A Note on Testing
Due to the nature of communication protocols, we tried to implement a thorough
set of unittests which tests:
- Message packing and unpacking
- Custom message's
- Message collisions and declaration errors
- Packet framing and unframing
- Corrupt packet handling and recovery

That being said, if you do find any bugs, please let us know by either creating
an issue so that we can resolve the issue for everyone.  

## Contributing
Obviously this is just a quick and dirty project; however, if you have any ideas,
critiques or changes just let me know or submit a pull request.

## License
Just like VESC, PyVESC is distributed under a
[Creative Commons ShareALike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).
