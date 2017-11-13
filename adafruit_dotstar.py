# The MIT License (MIT)
#
# Copyright (c) 2016 Damien P. George (original Neopixel object)
# Copyright (c) 2017 Ladyada
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries
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
`adafruit_dotstar` - DotStar strip driver
====================================================

* Author(s): Damien P. George, Limor Fried & Scott Shawcroft
"""
import busio
import digitalio
import math
import time

class DotStar:
    """
    A sequence of dotstars.

    :param ~microcontroller.Pin clock: The pin to output dotstar clock on.
    :param ~microcontroller.Pin data: The pin to output dotstar data on.
    :param int n: The number of dotstars in the chain
    :param float brightness: Brightness of the pixels between 0.0 and 1.0
    :param bool auto_write: True if the dotstars should immediately change when set. If False, `show` must be called explicitly.


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

    def __init__(self, clock, data, n, brightness=1.0, auto_write=True):
        self.spi = None
        try:
            self.spi = busio.SPI(clock, MOSI=data)
            while not self.spi.try_lock():
                pass
            self.spi.configure(baudrate=4000000)
        except ValueError:
            self.dpin = digitalio.DigitalInOut(data)
            self.cpin = digitalio.DigitalInOut(clock)
            self.dpin.direction = digitalio.Direction.OUTPUT
            self.cpin.direction = digitalio.Direction.OUTPUT
            self.cpin.value = False
        self.n = n
        self.start_header_size = 4
        # Supply one extra clock cycle for each two pixels in the strip.
        self.end_header_size = n // 16
        if n % 16 != 0:
            self.end_header_size += 1
        self.buf = bytearray(n * 4 + self.start_header_size + self.end_header_size)
        self.end_header_index = len(self.buf) - self.end_header_size;

        # Four empty bytes to start.
        for i in range(self.start_header_size):
            self.buf[i] = 0x00
        # Mark the beginnings of each pixel.
        for i in range(self.start_header_size, self.end_header_index, 4):
            self.buf[i] = 0xff
        # 0xff bytes at the end.
        for i in range(self.end_header_index, len(self.buf)):
            self.buf[i] = 0xff
        self.brightness = brightness
        self.auto_write = auto_write

    def deinit(self):
        """Blank out the DotStars and release the resources."""
        self.auto_write = False
        for i in range(self.start_header_size, self.end_header_index):
            if i % 4 != 0:
                self.buf[i] = 0
        self.show()
        if self.spi:
            self.spi.deinit()
        else:
            self.dpin.deinit()
            self.cpin.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    def _set_item(self, index, value):
        offset = index * 4 + self.start_header_size
        r = 0
        g = 0
        b = 0
        if type(value) == int:
            r = value >> 16
            g = (value >> 8) & 0xff
            b = value & 0xff
        else:
            r, g, b = value
        # Each pixel starts with 0xFF, then red/green/blue. Although the data
        # sheet suggests using a global brightness in the first byte, we don't
        # do that because it causes further issues with persistence of vision
        # projects.
        self.buf[offset] = 0xff    # redundant; should already be set
        self.buf[offset + 1] = b
        self.buf[offset + 2] = g
        self.buf[offset + 3] = r

    def __setitem__(self, index, val):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            length = stop - start
            if step != 0:
                length = math.ceil(length / step)
            if len(val) != length:
                raise ValueError("Slice and input sequence size do not match.")
            for val_i, in_i in enumerate(range(start, stop, step)):
                self._set_item(in_i, val[val_i])
        else:
            self._set_item(index, val)

        if self.auto_write:
            self.show()

    def __getitem__(self, index):
        if isinstance(index, slice):
            out = []
            for in_i in range(*index.indices(len(self.buf) // 4)):
                out.append(tuple(self.buf[in_i * 4 + (3 - i) + self.start_header_size]
                           for i in range(3)))
            return out
        if index < 0:
            index += len(self)
        if index >= self.n or index < 0:
            raise IndexError
        offset = index * 4
        return tuple(self.buf[offset + (3 - i) + self.start_header_size]
                     for i in range(3))

    def __len__(self):
        return self.n

    @property
    def brightness(self):
        """Overall brightness of the pixel"""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        self._brightness = min(max(brightness, 0.0), 1.0)

    def fill(self, color):
        """Colors all pixels the given ***color***."""
        auto_write = self.auto_write
        self.auto_write = False
        for i in range(len(self)):
            self[i] = color
        if auto_write:
            self.show()
        self.auto_write = auto_write

    def ds_writebytes(self, buf):
        for b in buf:
            for i in range(8):
                self.cpin.value = True
                self.dpin.value = (b & 0x80)
                self.cpin.value = False
                b = b << 1

    def show(self):
        """Shows the new colors on the pixels themselves if they haven't already
        been autowritten.

        The colors may or may not be showing after this function returns because
        it may be done asynchronously."""
        # Create a second output buffer if we need to compute brightness
        buf = self.buf
        if self.brightness < 1.0:
            buf = bytearray(self.buf)
            # Four empty bytes to start.
            for i in range(self.start_header_size):
                buf[i] = 0x00
            for i in range(self.start_header_size, self.end_header_index):
                buf[i] = self.buf[i] if i %4 == 0 else int(self.buf[i] * self._brightness)
            # Four 0xff bytes at the end.
            for i in range(self.end_header_index, len(buf)):
                buf[i] = 0xff

        if self.spi:
            self.spi.write(buf)
        else:
            self.ds_writebytes(buf)
            self.cpin.value = False
