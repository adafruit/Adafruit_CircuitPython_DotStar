# PixelOrder is unused but I want people to be able to import it from here
from adafruit_dotstar import DotStar, START_HEADER_SIZE, PixelOrder
from math import ceil
"""
This is different than the standard Adafruit Dotstar library because it
allows you to use the hardware brightness value on a per-pixel basis.
This is functionality the Neopixel does not support, and the standard
adafruit dotstar/neopixel libraries should match.

The brightness argument here is the default brightness of each pixel, but
you can override it if you use set_pixel
"""

LED_START = 0b11100000  # Three "1" bits, followed by 5 brightness bits


class AdvancedDotStar(DotStar):

    def _set_item(self, index, value):
        """
            value can be either a (r,g,b) tuple, or (r,g,b, brightness)
            brightness should be a float

        Set a pixel value. You can use brightness here, if it's not passed it
        will default to the strip's 'brightness' setting.

        Important notes about the per-pixel brightness - it's accomplished by
        PWMing the entire output of the LED, and that PWM is at a much
        slower clock than the rest of the LEDs. This can cause problems in
        Persistence of Vision Applications

        """

        offset = index * 4 + START_HEADER_SIZE
        rgb = value

        if len(value) == 4:
            brightness = value[-1]
            rgb = value[:3]
        else:
            brightness = self.brightness

        brightness_byte = ceil(brightness * 31) & 0b00011111
        # LED startframe is three "1" bits, followed by 5 brightness bits

        self._buf[offset] = brightness_byte | LED_START
        self._buf[offset + 1] = rgb[self.pixel_order[0]]
        self._buf[offset + 2] = rgb[self.pixel_order[1]]
        self._buf[offset + 3] = rgb[self.pixel_order[2]]

        if self.auto_write:
            self.show()

    def show(self):
        """
        Override parent show method because we don't do the float brightness
        correction anymore.
        """

        if self._spi:
            self._spi.write(self._buf)
        else:
            self._ds_writebytes(self._buf)
            self.cpin.value = False
