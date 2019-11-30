
Adafruit CircuitPython DotStar
==============================

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-dotstar/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/dotstar/en/latest/
    :alt: Documentation Status

.. image :: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_DotStar.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_DotStar
    :alt: Build Status

Higher level DotStar driver that presents the strip as a sequence. It is the
same api as the `NeoPixel library <https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel>`_.

Colors are stored as tuples by default. However, you can also use int hex syntax
to set values similar to colors on the web. For example, ``0x100000`` (``#100000``
on the web) is equivalent to ``(0x10, 0, 0)``.

If you send a tuple with 4 values, you can control the brightness value, which appears in DotStar but not NeoPixels.
It should be a float. For example, (0xFF,0,0, 1.0) is the brightest red possible, (1,0,0,0.01) is the dimmest red possible.

.. note:: The int hex API represents the brightness of the white pixel when
  present by setting the RGB channels to identical values. For example, full
  white is 0xffffff but is actually (0xff, 0xff, 0xff) in the tuple syntax. 

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-dotstar/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-dotstar

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-dotstar

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-dotstar

Usage Example
=============

This example demonstrates the library with the single built-in DotStar on the
`Trinket M0 <https://www.adafruit.com/product/3500>`_ and
`Gemma M0 <https://www.adafruit.com/product/3501>`_.

.. code-block:: python

    import board
    import adafruit_dotstar

    pixels = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
    pixels[0] = (10, 0, 0)


This example demonstrates the library with the DotStar Feather Wing and bounces Blinka.

`Feather M4 Express <https://www.adafruit.com/product/3857>`_ and
`DotStar FeatherWing <https://www.adafruit.com/product/3449>`_.

.. code-block:: python

    import board
    import adafruit_dotstar
    import time


    import adafruit_dotstar
    dotstar = adafruit_dotstar.DotStar(board.D13, board.D11, 72,
                                       pixel_order=adafruit_dotstar.BGR,
                                       brightness=0.3, auto_write=False)

    blinka = (
        (0, 0x0f0716, 0x504069, 0x482e63, 0, 0),
        (0, 0x3d1446, 0x502b74, 0x622f8c, 0, 0),
        (0, 0x2e021b, 0x2e021b, 0x2e021b, 0, 0),
        (0, 0, 0x2e021b, 0x2e021b, 0, 0),
        (0, 0x591755, 0x912892, 0x3f205c, 0x282828, 0x301844),
        (0x65206b, 0x932281, 0x6e318f, 0x6d2b7e, 0x7e2686, 0x8c2c8f),
        (0x7c2d8c, 0xa21c81, 0x6b308e, 0x74257b, 0x7b2482, 0x742f8d),
        (0x23051a, 0x5c0f45, 0x81227b, 0x551a5b, 0x691b5d, 0x4d0c39),
    )
    offset = 0
    direction = 1
    while True:
        dotstar.fill(0)
        for y, row in enumerate(blinka):
            for x, value in enumerate(row):
                n = x * 12 + (y + offset)
                dotstar[n] = row[x]
        dotstar.show()
        time.sleep(0.1)
        offset += direction
        if offset > 4 or offset < 0:
            direction = -direction
            offset += direction


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
