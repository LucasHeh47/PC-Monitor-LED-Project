import time
import board
import neopixel
from hdmi import get_average_screen_color
from enum import Enum

NUM_LEDS = 123
LEFT_LEDS = 23
TOP_LEDS = 39
RIGHT_LEDS = 21
BOTTOM_LEDS = 41


class Color(Enum):
    RED     = (255, 0, 0)
    GREEN   = (0, 255, 0)
    BLUE    = (0, 0, 255)
    WHITE   = (255, 255, 255)
    BLACK   = (0, 0, 0)
    YELLOW  = (255, 255, 0)
    CYAN    = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE  = (255, 165, 0)
    PURPLE  = (128, 0, 128)
    PINK    = (255, 105, 180)
    TEAL    = (0, 128, 128)


pixels = neopixel.NeoPixel(board.D18, NUM_LEDS, auto_write=False)

def wheel(pos):
        if pos < 85:
                return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
                pos -= 85
                return (255 - pos * 3, 0, pos * 3)
        else:
                pos -= 170
                return (0, pos * 3, 255 - pos * 3)

def rainbow():
    while True:
            for j in range(255):
                    for i in range(NUM_LEDS):
                            pixel_index = (i * 256 // NUM_LEDS) + j
                            pixels[i] = wheel(pixel_index & 255)
                    pixels.show()
                    time.sleep(0.02)

def solid(r, g, b):
    for i in range(NUM_LEDS):
        pixels[i] = (r, g, b)
    pixels.show()

def solid(color):
    for i in range(NUM_LEDS):
        pixels[i] = color
    pixels.show()

def breathing(colors, speed):
    while True:
        brightness_steps = 100  # Number of brightness levels in and out
        for color in colors:
            r, g, b = color.value

            # Fade in
            for i in range(brightness_steps):
                factor = i / brightness_steps
                for j in range(NUM_LEDS):
                    pixels[j] = (int(r * factor), int(g * factor), int(b * factor))
                pixels.show()
                time.sleep(speed)

            # Fade out
            for i in range(brightness_steps, -1, -1):
                factor = i / brightness_steps
                for j in range(NUM_LEDS):
                    pixels[j] = (int(r * factor), int(g * factor), int(b * factor))
                pixels.show()
                time.sleep(speed)


#breathing((Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW), 0.02)
while True:
    color = get_average_screen_color(1000)
    solid(color)
    time.sleep(0.5)