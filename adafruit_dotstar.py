# The MIT License (MIT)
#
# Copyright (c) 2016 Damien P. George (original Neopixel object)
# Copyright (c) 2017 Ladyada
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries
# Copyright (c) 2019 Roy Hooper
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`adafruit_dotstar` - DotStar strip driver (for CircuitPython 5.0+ with _pixelbuf)
=================================================================================

* Author(s): Damien P. George, Limor Fried, Scott Shawcroft & Roy Hooper
"""
import busio
import digitalio
try:
    import _pixelbuf
except ImportError:
    import adafruit_pypixelbuf as _pixelbuf

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DotStar.git"

START_HEADER_SIZE = 4

RBG = 'PRBG'
RGB = 'PRGB'
GRB = 'PGRB'
GBR = 'PGBR'
BRG = 'PBRG'
BGR = 'PBGR'
BGR = 'PBGR'


class DotStar(_pixelbuf.PixelBuf):
    """
    A sequence of dotstars.

    :param ~microcontroller.Pin clock: The pin to output dotstar clock on.
    :param ~microcontroller.Pin data: The pin to output dotstar data on.
    :param int n: The number of dotstars in the chain
    :param float brightness: Brightness of the pixels between 0.0 and 1.0
    :param bool auto_write: True if the dotstars should immediately change when
        set. If False, `show` must be called explicitly.
    :param str pixel_order: Set the pixel order on the strip - different
         strips implement this differently. If you send red, and it looks blue
         or green on the strip, modify this! It should be one of the values above.
    :param int baudrate: Desired clock rate if using hardware SPI (ignored if
        using 'soft' SPI). This is only a recommendation; the actual clock
        rate may be slightly different depending on what the system hardware
        can provide.

    Example for Gemma M0:

    .. code-block:: python

        import adafruit_dotstar
        import time
        from board import *

        RED = 0x100000

        with adafruit_dotstar.DotStar(APA102_SCK, APA102_MOSI, 1) as pixels:
            pixels[0] = RED
            time.sleep(2)
    """

    def __init__(self, clock, data, n, *, brightness=1.0, auto_write=True,
                 pixel_order=BGR, baudrate=4000000):
        self._spi = None
        try:
            self._spi = busio.SPI(clock, MOSI=data)
            while not self._spi.try_lock():
                pass
            self._spi.configure(baudrate=baudrate)

        except (NotImplementedError, ValueError):
            self.dpin = digitalio.DigitalInOut(data)
            self.cpin = digitalio.DigitalInOut(clock)
            self.dpin.direction = digitalio.Direction.OUTPUT
            self.cpin.direction = digitalio.Direction.OUTPUT
            self.cpin.value = False
        self.n = n

        # Supply one extra clock cycle for each two pixels in the strip.
        end_header_size = n // 16
        if n % 16 != 0:
            end_header_size += 1
        bufsize = 4 * n + START_HEADER_SIZE + end_header_size
        end_header_index = bufsize - end_header_size
        self.pixel_order = pixel_order

        self._buf = bytearray(bufsize)
        self._rawbuf = bytearray(bufsize)

        # Four empty bytes to start.
        for i in range(START_HEADER_SIZE):
            self._rawbuf[i] = 0x00
        # 0xff bytes at the end.
        for i in range(end_header_index, bufsize):
            self._rawbuf[i] = 0xff
        # Mark the beginnings of each pixel.
        for i in range(START_HEADER_SIZE, end_header_index, 4):
            self._rawbuf[i] = 0xff
        self._buf[:] = self._rawbuf[:]

        super(DotStar, self).__init__(n, self._buf, byteorder=pixel_order,
                                      rawbuf=self._rawbuf, offset=START_HEADER_SIZE,
                                      brightness=brightness, auto_write=auto_write)

    def show(self):
        """Shows the new colors on the pixels themselves if they haven't already
        been autowritten.

        The colors may or may not be showing after this method returns because
        it may be done asynchronously.

        This method is called automatically if auto_write is set to True.
        """
        if self._spi:
            self._spi.write(self._buf)
        else:
            self.ds_writebytes()

    def _ds_writebytes(self):
        for b in self.buf:
            for _ in range(8):
                self.dpin.value = (b & 0x80)
                self.cpin.value = True
                self.cpin.value = False
                b = b << 1
        self.cpin.value = False

    def deinit(self):
        """Blank out the DotStars and release the resources."""
        self.fill(0)
        self.show()
        if self._spi:
            self._spi.deinit()
        else:
            self.dpin.deinit()
            self.cpin.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    def fill(self, color):
        """Colors all pixels the given ***color***."""
        _pixelbuf.fill(self, color)
