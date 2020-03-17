#!/usr/bin/python3

# Persistence-of-vision (POV) example for Adafruit DotStar RGB LED strip.
# Loads image, displays column-at-a-time on LEDs at very high speed,
# suitable for naked-eye illusions.
# See dotstar_simpletest.py for a much simpler example script.
# See dotstar_image_paint.py for a slightly simpler light painting example.
# This code accesses some elements of the dotstar object directly rather
# than through function calls or setters/getters...this is poor form as it
# could break easily with future library changes, but is the only way right
# now to do the POV as quickly as possible.

import board
from PIL import Image
import adafruit_dotstar as dotstar

NUMPIXELS = 30  # Length of DotStar strip
FILENAME = "hello.png"  # Image file to load
ORDER = dotstar.BGR  # Change to GBR for older DotStar strips

# First two arguments in strip declaration identify the clock and data pins
# (here we're using the hardware SPI pins).
DOTS = dotstar.DotStar(
    board.SCK,
    board.MOSI,
    NUMPIXELS,
    auto_write=False,
    brightness=0.25,
    pixel_order=ORDER,
)

# Load image in RGB format and get dimensions:
print("Loading...")
IMG = Image.open(FILENAME).convert("RGB")
PIXELS = IMG.load()
WIDTH = IMG.size[0]
HEIGHT = IMG.size[1]
print("%dx%d pixels" % IMG.size)

if HEIGHT > NUMPIXELS:
    HEIGHT = NUMPIXELS

# Calculate gamma correction table, makes mid-range colors look 'right':
GAMMA = bytearray(256)
for i in range(256):
    # Notice we access DOTS.brightness directly here...the gamma table will
    # handle any brightness-scaling, so we can set the object brightness back
    # to max and it won't need to perform brightness scaling on every write.
    GAMMA[i] = int(pow(float(i) / 255.0, 2.7) * DOTS.brightness * 255.0 + 0.5)
DOTS.brightness = 1.0

# Allocate list of bytearrays, one for each column of image.
# Each pixel REQUIRES 4 bytes (0xFF, B, G, R).
print("Allocating...")
COLUMN = [0 for x in range(WIDTH)]
for x in range(WIDTH):
    COLUMN[x] = bytearray(HEIGHT * 4)

# Convert entire RGB image into column-wise bytearray list.
# The dotstar_image_paint.py example uses the library's 'setter' operation
# for each pixel to do any R/G/B reordering.  Because we're preparing data
# directly for the strip, there's a reference to 'ORDER' here to rearrange
# the color bytes as needed.
print("Converting...")
for x in range(WIDTH):  # For each column of image
    for y in range(HEIGHT):  # For each pixel in column
        value = PIXELS[x, y]  # Read RGB pixel in image
        y4 = y * 4  # Position in raw buffer
        COLUMN[x][y4] = 0xFF  # Pixel start marker
        y4 += 1  # Pixel color data start
        COLUMN[x][y4 + ORDER[0]] = GAMMA[value[0]]  # Gamma-corrected R
        COLUMN[x][y4 + ORDER[1]] = GAMMA[value[1]]  # Gamma-corrected G
        COLUMN[x][y4 + ORDER[2]] = GAMMA[value[2]]  # Gamma-corrected B

print("Displaying...")
while True:  # Loop forever

    # pylint: disable=protected-access
    # (Really shouldn't access _buf directly, but needed for fastest POV)
    for x in range(WIDTH):  # For each column of image...
        DOTS._buf[4 : 4 + HEIGHT * 4] = COLUMN[x]  # Copy column to DotStar buffer
        DOTS.show()  # Send data to strip
