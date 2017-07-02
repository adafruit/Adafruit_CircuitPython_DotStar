# DotStar driver for CircuitPython 
# MIT license; Copyright (c) 2017 Ladyada & Damein George (original Neopixel object)

import digitalio
import time

class DotStar:
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

    def set_brightness(self, range):
        if (range > 1.0):
            self.brightness = 1.0
        elif (range < 0):
            self.brightness = 0.0
        else:
            self.brightness = range

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

    def write(self):
        # Tell strip we're ready with many 0x00's
        self.ds_writebytes([0x00, 0x00, 0x00, 0x00])
        for i in range(self.n):
            # each pixel starts with 0xFF, then red/green/blue
            pixel = [0xFF, 0, 0, 0]
            # scale each pixel by the brightness
            for x in range(3):
                pixel[x+1] = int(self.buf[i * self.bpp + x] * self.brightness)
            # write this pixel
            self.ds_writebytes(pixel)
        # Tell strip we're done with many 0xFF's
        self.ds_writebytes([0xFF, 0xFF, 0xFF, 0xFF])
        self.cpin.value = False
