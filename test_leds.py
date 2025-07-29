import time
import board
import neopixel


NUM_LEDS = 123
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

while True:
	for j in range(255):
		for i in range(NUM_LEDS):
			pixel_index = (i * 256 // NUM_LEDS) + j
			pixels[i] = wheel(pixel_index & 255)
		pixels.show()
		time.sleep(0.02)
