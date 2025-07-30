import threading
import time
import board
import neopixel
import socket
import json
from hdmi import get_average_screen_color, init_sample_points, release_capture, get_all_led_colors
from enum import Enum

NUM_LEDS = 123
LEFT_LEDS = 23
TOP_LEDS = 39
RIGHT_LEDS = 20
BOTTOM_LEDS = 41

animating = False
animation_thread = None


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
    global animating
    animating = True
    while animating:
            for j in range(255):
                    for i in range(NUM_LEDS):
                            pixel_index = (i * 256 // NUM_LEDS) + j
                            pixels[i] = wheel(pixel_index & 255)
                    pixels.show()
                    time.sleep(0.02)

def solid(r, g, b):
    global animating
    animating = True
    while animating:
        for i in range(NUM_LEDS):
            pixels[i] = (r, g, b)
        pixels.show()

def solid(color):
    global animating
    animating = True
    while animating:
        for i in range(NUM_LEDS):
            pixels[i] = color
        pixels.show()

def breathing(colors, speed):
    global animating
    animating = True
    while animating:
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

def light_sides(side_colors: dict):
    # Use .value if using Color enum
    def get_rgb(c):
        return c.value if isinstance(c, Color) else c

    # Define segment start indices
    left_start = 0
    top_start = left_start + LEFT_LEDS
    right_start = top_start + TOP_LEDS
    bottom_start = right_start + RIGHT_LEDS

    # Map each side to its range of LED indices
    side_ranges = {
        "left":   range(left_start, top_start),
        "top":    range(top_start, right_start),
        "right":  range(right_start, bottom_start),
        "bottom": range(bottom_start, NUM_LEDS),
    }

    # Clear all LEDs first
    for i in range(NUM_LEDS):
        pixels[i] = (0, 0, 0)

    # Set colors for each specified side
    for side, color in side_colors.items():
        rgb = get_rgb(color)
        if side in side_ranges:
            for i in side_ranges[side]:
                pixels[i] = rgb

    pixels.show()


def snake_animation(colors, length, delay=0.05):
    num_colors = len(colors)
    heads = [(i * NUM_LEDS) // num_colors for i in range(num_colors)]  # even spacing

    global animating
    animating = True
    while animating:
        # Clear strip
        for i in range(NUM_LEDS):
            pixels[i] = (0, 0, 0)

        # Draw each snake
        for snake_index, color in enumerate(colors):
            head = heads[snake_index]
            r, g, b = color

            for i in range(length):
                pos = (head - i) % NUM_LEDS
                pixels[pos] = (r, g, b)

            # Move head forward
            heads[snake_index] = (head + 1) % NUM_LEDS

        pixels.show()
        time.sleep(delay)

def generate_led_positions(screen_width, screen_height):
    positions = []

    # Bottom (starts bottom-left)
    for i in range(BOTTOM_LEDS):
        x = int((i / BOTTOM_LEDS) * screen_width)
        y = screen_height - 1
        positions.append((x, y))

    # Right (bottom to top)
    for i in range(RIGHT_LEDS):
        x = screen_width - 1
        y = int(screen_height - (i / RIGHT_LEDS) * screen_height)
        positions.append((x, y))

    # Top (right to left)
    for i in range(TOP_LEDS):
        x = int(screen_width - (i / TOP_LEDS) * screen_width)
        y = 0
        positions.append((x, y))

    # Left (top to bottom)
    for i in range(LEFT_LEDS):
        x = 0
        y = int((i / LEFT_LEDS) * screen_height)
        positions.append((x, y))

    return positions


def handle_JSON(json):
    global animating

    if "animation" not in json or "colors" not in json:
        print("Missing 'animation' or 'colors' field in JSON")
        return

    animating = False

    animation_type = json["animation"]
    color_names = json["colors"]

    # Convert color names to RGB tuples
    try:
        color_values = [Color[name.upper()].value for name in color_names]
    except KeyError as e:
        print(f"Invalid color name: {e}")
        return

    if animation_type == "solid":
        solid(color_values[0])  # Only one color used
    elif animation_type == "breathing":
        speed = float(json.get("speed", 0.05))
        breathing([Color(name.upper()) for name in color_names], speed)
    elif animation_type == "snake":
        speed = float(json.get("speed", 0.05))
        snake_animation(color_values, length=10, delay=speed)
    else:
        print(f"Unknown animation type: {animation_type}")

def handle_JSON(json):
    global animating, animation_thread

    if "animation" not in json or "colors" not in json:
        print("Missing 'animation' or 'colors' field in JSON")
        return

    # Stop previous animation
    stop_animation()

    animation_type = json["animation"]
    color_names = json["colors"]

    try:
        color_values = [Color[name.upper()].value for name in color_names]
    except KeyError as e:
        print(f"Invalid color name: {e}")
        return

    if animation_type == "solid":
        solid(color_values[0])
    elif animation_type == "breathing":
        def run_breathing():
            breathing([Color(name.upper()) for name in color_names], float(json.get("speed", 0.05)))
        animation_thread = threading.Thread(target=run_breathing)
        animation_thread.start()
    elif animation_type == "snake":
        def run_snake():
            snake_animation(color_values, length=10, delay=float(json.get("speed", 0.05)))
        animation_thread = threading.Thread(target=run_snake)
        animation_thread.start()
    else:
        print(f"Unknown animation type: {animation_type}")

def stop_animation():
    global animating, animation_thread
    animating = False
    if animation_thread and animation_thread.is_alive():
        animation_thread.join()


#breathing((Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW), 0.02)

# try:
#     init_sample_points(sample_count=200)
#     while True:
#         color = get_average_screen_color()
#         solid(color)
# except KeyboardInterrupt:
#     release_capture()

# led_positions = generate_led_positions(2560, 1440)
#
# while True:
#     colors = get_all_led_colors(led_positions)
#     for i in range(NUM_LEDS):
#         pixels[i] = colors[i]
#     pixels.show()
#     time.sleep(0.05)

listener_thread = threading.Thread(target=json_listener_thread, daemon=True)
listener_thread.start()

#snake_animation([Color.BLUE.value, Color.RED.value, Color.BLUE.value, Color.RED.value], length=20)

# light_sides({
#     "top": Color.BLUE,
#     "bottom": Color.BLUE,
#     "left": Color.RED,
#     "right": Color.RED
# })
