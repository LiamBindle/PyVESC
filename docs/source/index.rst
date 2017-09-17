PyVESC Documentation
********************

.. toctree::
  :titlesonly:


PyVESC is aimed at being a easy to use and robust python implementation of the
communication protocol used by the
`VESC - Open Source ESC <http://vedder.se/2015/01/vesc-open-source-esc/>`_
project by Benjamin Vedder. Its a great project with a really great community
and I'd urge anyone interested in motor controllers to take a look at it.

That being said, if you're here you probably already know about it. This small
project was written by Liam Bindle for the
`University of Saskatchewan Space Design Team <https://usst.ca>`_
as our primary language for non-embedded system is Python. You might wonder why
you might need a library to handling packing and parsing VESC messages since
Pythons standard
`struct <https://docs.python.org/3.5/library/struct.html>`_
module is great for almost exaclty this. PyVESC's usefulness comes from the fact
that PyVESC is:

* Well tested
* Robust in handling corrupt packets in a buffer
* Messages are easily extensible so that PyVESC can be used as a generic
  message/codec protocol (ie. at the USST we use PyVESC for sending messages to
  all of our embedded systems by `Implementing Additional Messages`_)
* Implements a number of common-error catching exceptions to speed up your
  development

Quick Example
=============
This is just a quick example of how PyVESC can be used. First lets see how
PyVESC can be used to go from a message (VESCMessage) to a packet (bytes).

.. code-block:: python

  # make a SetDutyCycle message
  my_msg = pyvesc.SetDutyCycle(1e5)
  print(my_msg.duty_cycle) # prints value of my_msg.duty_cycle
  my_packet = pyvesc.encode(my_msg)
  # my_packet (type: bytes) can now be sent over your UART connection

Now lets look at how we can parse messages from a buffer (assuming the buffer is
being filled by your UART connection)

.. code-block:: python

  # buff is bytes filled from your UART connection
  my_msg, consumed = pyvesc.decode(buff)
  buff = buff[consumed:]  # remove consumed bytes from the buffer
  if my_msg:
    print(my_msg.duty_cycle)    # prints value of my_msg.duty_cycle

Installation
============
PyVESC is available on the `Python Package Index <https://pypi.python.org/pypi/pyvesc>`_.

.. code-block:: bash

  pip install pyvesc

Usage
=====
PyVESC serves two purposes:

#. Allows messages to be created and manipulated easily
#. Performs message encoding (to packet) and robust message decoding (to message object)

Messages
========
Here is a list of the messages currently supported in PyVESC. Note that not all
of VESC's messages are implemented. This is because we have only implemented the
messages we use as we don't want to distribute anything that hasn't been tested.
If you need additional VESC messages, they are very easy to implement (and we'd
greatly appreciate a pull request after). For more infromation see
`Implementing Additional Messages`_.

It should be noted that all message objects can be created in 3 ways:

#. No constructor arguments
#. Variadic arguments (field values)
#. From decoding the next packet in a buffer

Setter Messages
===============
These are the setter messages which are currently implemented.

.. autoclass:: pyvesc.SetDutyCycle
.. autoclass:: pyvesc.SetRPM
.. autoclass:: pyvesc.SetCurrent
.. autoclass:: pyvesc.SetCurrentBrake
.. autoclass:: pyvesc.SetPosition
.. autoclass:: pyvesc.SetRotorPositionMode

Getter Messages
===============
These are the getters that are currently implemented.

.. autoclass:: pyvesc.GetValues
.. autoclass:: pyvesc.GetRotorPosition

Implementing Additional Messages
================================
Here we'll take a look at how to implement your own messages. You're message
class must have the metaclass `pyvesc.VESCMessage`. In addition to this you must
define two static attributes:

#. `id` (uint8): The ID for your message
#. `fields` (list of tuples): Declaration of the fields your message has. Each
   element in the list declares a field. The first element of the field tuple is
   the name of the field (type: str), and the second element is the field type
   `format characters <https://docs.python.org/3.5/library/struct.html#format-characters>`_.

This is probably easiest explained with an example. Here is the declaration of
the SetDutyCycle message.

.. code-block:: python

  class SetDutyCycle(metaclass=pyvesc.VESCMessage):
      id = 5
      fields = [
          ('duty_cycle', 'i')
      ]

That's it! Taking a look at the declaration we see:

* The message's ID is 5
* The message has a single field with a name `duty_cycle` and type int (this
  is what the
  `format characters <https://docs.python.org/3.5/library/struct.html#format-characters>`_
  `'i'` is)

If you are interested in the details of how this works, the `pyvesc.VESCMessage`
metaclass has a registry of all its children this registry is a dictionary
with key's being the messages ID and values being the messages class. This
metaclass also ensures that you define both fields and check that the ID is
unique.


Encoding
========
The following is the function call you should use to get a
packet for your message.

.. autofunction:: pyvesc.encode

Encoding is done by first serializing the message object and then framing it
in a VESC packet.

Decoding
========
The following is the function you should call to decode messages from the
buffer.

.. autofunction:: pyvesc.decode

Decoding is done by checking if the buffer has a full VESC packet which can be
parsed. If it does then we begin parsing it, else we return having consumed 0
bytes from the buffer. To parse a message we must parse the packet payload,
construct a message object from the payload's ID and then fill the message's
fields values. In addition to this we must ensure that if the integrity of the
packet has been comprimised (by checking CRC or packet framing), we properly
handle recoving our location in the buffer so that subsequent packets are
retained.

Contributing
============
Pull request are always welcome! If you have implemented any additional messages
and tested that they are working properly feel free to make a pull request so we
can have it availible to everyone.

In addition to this, if you discover any bugs please
`create an issue <https://github.com/LiamBindle/PyVESC/issues/new>`_ so that we
can resolve it for everyone.

Find our repository here: `<https://github.com/LiamBindle/PyVESC>`_.

License
=======
PyVESC is distributed under a
`Creative Commons ShareALike 4.0 International License <https://creativecommons.org/licenses/by-sa/4.0/>`_.
