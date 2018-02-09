import time
import random
import board
import adafruit_dotstar as dotstar

# One pixel connected internally on a GEMMA M0
dots = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)

# With a Dotstar Digital LEB Strip with 30 lights
#dots = dotstar.DotStar(board.SCK, board.MOSI, 30, brightness=0.2)

######################### HELPERS ##############################

# a random color 0 -> 224
def random_color():
    return random.randrange(0, 7) * 32

######################### MAIN LOOP ##############################
n_dots = len(dots)
while True:
    #fill each dot with a random color
    for dot in range(n_dots):
        dots[dot] = (random_color(), random_color(), random_color())

    # show all dots in strip
    dots.show()

    time.sleep(.25)
