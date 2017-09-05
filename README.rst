
Adafruit CircuitPython DotStar
==============================

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-neopixel/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/neopixel/en/latest/
    :alt: Documentation Status

.. image :: https://badges.gitter.im/adafruit/circuitpython.svg
    :target: https://gitter.im/adafruit/circuitpython?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
    :alt: Gitter

.. image :: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

Higher level DotStar driver that presents the strip as a sequence. It is the
same api as the `NeoPixel library <https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel>`_.

Colors are stored as tuples by default. However, you can also use int hex syntax
to set values similar to colors on the web. For example, ``0x100000`` (``#100000``
on the web) is equivalent to ``(0x10, 0, 0)``.

.. note:: The int hex API represents the brightness of the white pixel when
  present by setting the RGB channels to identical values. For example, full
  white is 0xffffff but is actually (0, 0, 0, 0xff) in the tuple syntax. Setting
  a pixel value with an int will use the white pixel if the RGB channels are
  identical. For full, independent, control of each color component use the
  tuple syntax.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

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

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

API Reference
=============

.. toctree::
   :maxdepth: 2

   api
