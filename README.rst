
Adafruit CircuitPython DotStar
==============================

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-dotstar/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/dotstar/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_DotStar/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_DotStar/actions/
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

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
    python3 -m venv .venv
    source .venv/bin/activate
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

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/dotstar/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
