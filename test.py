import time
import board
import neopixel

# Adjust this to match how many LEDs you actually have connected
NUM_LEDS = 50

pixels = neopixel.NeoPixel(board.D18, NUM_LEDS, auto_write=True)

# Clear strip
pixels.fill((0, 0, 0))
time.sleep(1)

# Test red
pixels.fill((255, 0, 0))
time.sleep(1)

# Test green
pixels.fill((0, 255, 0))
time.sleep(1)

# Test blue
pixels.fill((0, 0, 255))
time.sleep(1)

# Clear
pixels.fill((0, 0, 0))
