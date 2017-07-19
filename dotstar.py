# DotStar driver for CircuitPython
# MIT license; Copyright (c) 2017 Ladyada & Damien George (original Neopixel object)

import digitalio
import time

class DotStar:
    """
    A sequence of dotstars.

    :param ~microcontroller.Pin data: The pin to output dotstar data on.
    :param ~microcontroller.Pin clock: The pin to output dotstar clock on.
    :param int n: The number of dotstars in the chain
    :param int bpp: Bytes per pixel (usually 3 or 4)
    :param float brightness: Brightness of the pixels between 0.0 and 1.0

    Example for Gemma M0:

    .. code-block:: python

        import dotstar
        from board import *

        RED = 0x100000

        with dotstar.DotStar(APA102_MOSI, APA102_SCK, 1) as pixels:
            pixels[0] = RED
            pixels.show()
    """

    ORDER = (1, 0, 2, 3)
    def __init__(self, data, clock, n, bpp=3, brightness=1.0):
        self.dpin = digitalio.DigitalInOut(data)
        self.cpin = digitalio.DigitalInOut(clock)
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        self.dpin.switch_to_output()
        self.cpin.switch_to_output()
        self.cpin.value = False
        self.brightness = brightness

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.dpin.deinit()
        self.cpin.deinit()

    def __setitem__(self, index, val):
        offset = index * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = val[i]

    def __getitem__(self, index):
        offset = index * self.bpp
        return tuple(self.buf[offset + self.ORDER[i]]
                     for i in range(self.bpp))

    def __len__(self):
        return self.n

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        self._brightness = min(max(brightness, 0.0), 1.0)

    def fill(self, color):
        for i in range(self.n):
            self[i] = color

    def ds_writebytes(self, bytes):
        for b in bytes:
            for i in range(8):
                self.cpin.value = True
                self.dpin.value = (b & 0x80)
                self.cpin.value = False
                b = b << 1

    def show(self):
        # Tell strip we're ready with many 0x00's
        self.ds_writebytes([0x00, 0x00, 0x00, 0x00])
        # Each pixel starts with 0xFF, then red/green/blue. Although the data
        # sheet suggests using a global brightness in the first byte, we don't
        # do that because it causes further issues with persistence of vision
        # projects.
        pixel = [0xFF, 0, 0, 0]
        for i in range(self.n):
            # scale each pixel by the brightness
            for x in range(3):
                pixel[x+1] = int(self.buf[i * self.bpp + x] * self._brightness)
            # write this pixel
            self.ds_writebytes(pixel)
        # Tell strip we're done with many 0xFF's
        self.ds_writebytes([0xFF, 0xFF, 0xFF, 0xFF])
        self.cpin.value = False
