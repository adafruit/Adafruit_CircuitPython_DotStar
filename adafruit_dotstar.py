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
`adafruit_dotstar` - DotStar strip driver (for CircuitPython 4.0+ with _pixelbuf)
=================================================================================

* Author(s): Damien P. George, Limor Fried, Scott Shawcroft, Roy Hooper
"""
import busio
import digitalio
try:
    from _pixelbuf import PixelBuf, RGB, RBG, GRB, GBR, BRG, BGR, LRGB, LRBG, LGRB, LGBR, LBRG, LBGR
except ImportError:
    from pypixelbuf import PixelBuf, RGB, RBG, GRB, GBR, BRG, BGR, LRGB, LRBG, LGRB, LGBR, LBRG, LBGR

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DotStar.git"

START_HEADER_SIZE = 4


class DotStar:
    """
    A sequence of dotstars.

    :param ~microcontroller.Pin clock: The pin to output dotstar clock on.
    :param ~microcontroller.Pin data: The pin to output dotstar data on.
    :param int n: The number of dotstars in the chain
    :param float brightness: Brightness of the pixels between 0.0 and 1.0
    :param bool auto_write: True if the dotstars should immediately change when
        set. If False, `show` must be called explicitly.
    :param ByteOrder pixel_order: Set the pixel order on the strip - different
         strips implement this differently. If you send red, and it looks blue
         or green on the strip, modify this! It should be one of the values above


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
        # for i in range(START_HEADER_SIZE, end_header_index, 4):
            # self._rawbuf[i] = 0xff
        self._buf[:] = self._rawbuf[:]

        writer = self._spi.write if self._spi else self._ds_writebytes
        def write_fn(*_):
            self._spi.write(self._buf)

        self._pb = PixelBuf(n, self._buf, byteorder=pixel_order,
            rawbuf=self._rawbuf, write_function=write_fn, offset=START_HEADER_SIZE, 
            write_args=(), brightness=brightness, auto_write=auto_write, dotstar=True)

        if self.auto_write:
            self.show()

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

    def _set_item(self, index, value):
        if isinstance(index, slice):
            start, stop, step = index.indices(self.n)
            self._pb[start:stop:step] = value
        self._pb[index] = value

    def __setitem__(self, index, value):
        """
        value can be one of three things:
                a (r,g,b) list/tuple
                a (r,g,b, brightness) list/tuple (if bpp=4, pixel_order=LBGR)
                a single, longer int that contains RGB values, like 0xFFFFFF
            brightness, if specified should be a float 0-1

        Set a pixel value. You can set per-pixel brightness here, if it's not passed it
        will use the max value for pixel brightness value, which is a good default.

        Important notes about the per-pixel brightness - it's accomplished by
        PWMing the entire output of the LED, and that PWM is at a much
        slower clock than the rest of the LEDs. This can cause problems in
        Persistence of Vision Applications
        """
        if isinstance(index, slice):
            start, stop, step = index.indices(self.n)
            self._pb[start:stop:step] = value
        self._pb[index] = value

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(self.n)
            return self._pb[start:stop:step]
        return self._pb[index]

    @property
    def brightness(self):
        return self._pb.brightness
    
    @brightness.setter
    def brightness(self, brightness):
        self._pb.brightness = brightness

    @property
    def auto_write(self):
        return self._pb.auto_write
    
    @auto_write.setter
    def auto_write(self, auto_write):
        self._pb.auto_write = auto_write

    def show(self):
        self._pb.show()

    def __len__(self):
        return self.n

    def fill(self, color):
        """Colors all pixels the given ***color***."""
        self._pb[0:self.n] = (color, ) * self.n

    def _ds_writebytes(self, buf):
        for b in buf:
            for _ in range(8):
                self.cpin.value = True
                self.dpin.value = (b & 0x80)
                self.cpin.value = False
                b = b << 1
        self.cpin.value = False
