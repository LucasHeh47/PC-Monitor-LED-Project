import threading
import time
import board
import neopixel
import socket
import json
from hdmi import get_average_screen_color, init_sample_points, release_capture
from enum import Enum

NUM_LEDS = 123
LEFT_LEDS = 23
TOP_LEDS = 39
RIGHT_LEDS = 21
BOTTOM_LEDS = 41

animating = False

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
    animating = True
    while animating:
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

def json_listener_thread(port=8888):
    global animating

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(1)
    print(f"Listening for JSON on port {port}...")

    while True:
        client, addr = server.accept()
        data = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk

        try:
            # Decode and split HTTP headers from body
            request = data.decode('utf-8')
            body = request.split("\r\n\r\n", 1)[1]

            json_data = json.loads(body)
            print("Received JSON:")
            print(json_data)
            handle_JSON(json_data)
        except (IndexError, json.JSONDecodeError) as e:
            print("Received invalid JSON")
            print("Error:", e)
        finally:
            client.close()

#breathing((Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW), 0.02)

# try:
#     init_sample_points(sample_count=200)
#     while True:
#         color = get_average_screen_color()
#         solid(color)
# except KeyboardInterrupt:
#     release_capture()

#listener_thread = threading.Thread(target=json_listener_thread, daemon=True)
#listener_thread.start()

#snake_animation([Color.BLUE.value, Color.RED.value, Color.GREEN.value, Color.YELLOW.value], length=10)

light_sides({
    "top": Color.BLUE,
    "bottom": Color.BLUE,
    "left": Color.RED,
    "right": Color.RED
})
