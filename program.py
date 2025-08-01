import threading
import time
import board
import neopixel
import socket
import json
from hdmi import release_capture, get_average_screen_color_fast
from color import Color

version = "1.1"

NUM_LEDS = 123
LEFT_LEDS = 23
TOP_LEDS = 39
RIGHT_LEDS = 20
BOTTOM_LEDS = 41

animating = False
animation_thread = None

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

def breathing(colors, speed, steps):
    global animating
    animating = True
    while animating:
        brightness_steps = steps  # Number of brightness levels in and out
        for color in colors:
            if not animating: return
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
        if isinstance(c, Color):
            return c.value
        elif isinstance(c, (list, tuple)) and len(c) == 3:
            return c
        print("Error reading RGB value: " + c)
        return (0, 0, 0)

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
        rgb = tuple(int(c) for c in get_rgb(color))
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

def average_screen_color():
    global animating
    animating = True
    try:
        while animating:
            color = get_average_screen_color_fast()
            for i in range(NUM_LEDS):
                pixels[i] = color
            pixels.show()
    except KeyboardInterrupt:
        release_capture()

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
    global animating, animation_thread

    if "add_color" in json:
        Color.add_custom_color(json["add_color"], json["r"], json["g"], json["b"])
        print(f"Adding color {json['add_color']} R:{json['r']} G:{json['g']} B:{json['b']}")
        return

    if "animation" not in json or "colors" not in json:
        print("Missing 'animation' or 'colors' field in JSON")
        return

    # Stop previous animation
    stop_animation()
    print("Stopped previous animation")

    animation_type = json["animation"]
    color_names = json["colors"]

    try:
        # These are ColorValue objects now
        color_values = [Color[name] for name in color_names]
    except KeyError as e:
        print(f"Invalid color name: {e}")
        return

    print(f"Starting new animation of: {animation_type} with colors: {color_names}")

    if animation_type == "solid":
        def run_solid():
            if len(color_values) == 1:
                color = color_values[0].value  # RGB tuple
            else:
                # Average the RGB values
                r = sum(c.value[0] for c in color_values) // len(color_values)
                g = sum(c.value[1] for c in color_values) // len(color_values)
                b = sum(c.value[2] for c in color_values) // len(color_values)
                color = (r, g, b)
            solid(color)
        animation_thread = threading.Thread(target=run_solid)

    elif animation_type == "breathing":
        def run_breathing():
            breathing(color_values, float(json.get("speed", 0.05)), int(json.get("steps", 100)))  # use ColorValue objects directly
        animation_thread = threading.Thread(target=run_breathing)

    elif animation_type == "snake":
        def run_snake():
            rgb_values = [c.value for c in color_values]
            snake_animation(rgb_values, length=int(json.get("length", 10)), delay=float(json.get("speed", 0.05)))
        animation_thread = threading.Thread(target=run_snake)

    elif animation_type == "average_screen_color":
        def run_avg_screen_color():
            average_screen_color()
        animation_thread = threading.Thread(target=run_avg_screen_color)

    elif animation_type == "rainbow":
        def run_rainbow():
            rainbow()
        animation_thread = threading.Thread(target=run_rainbow)

    elif animation_type == "sides":
        def run_sides():
            light_sides({
                # colors 1 2 3 and 4 are left top right bottom
                "left": color_names[0],
                "top": color_names[1],
                "right": color_names[2],
                "bottom": color_names[3]
            })
        animation_thread = threading.Thread(target=run_sides)

    else:
        print(f"Unknown animation type: {animation_type}")
        return

    animation_thread.start()


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
            # Directly decode raw JSON data
            json_data = json.loads(data.decode('utf-8'))
            print("Received JSON:")
            print(json_data)
            handle_JSON(json_data)
        except json.JSONDecodeError as e:
            print("Received invalid JSON")
            print("Error:", e)
        finally:
            client.close()


def stop_animation():
    global animating, animation_thread
    animating = False
    if animation_thread and animation_thread.is_alive():
        animation_thread.join()


#breathing((Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW), 0.02)

# led_positions = generate_led_positions(2560, 1440)
#
# while True:
#     colors = get_all_led_colors(led_positions)
#     for i in range(NUM_LEDS):
#         pixels[i] = colors[i]
#     pixels.show()
#     time.sleep(0.05)
print("V-", version)
Color.load_custom_colors()

listener_thread = threading.Thread(target=json_listener_thread, daemon=True)
listener_thread.start()

Color.save_custom_colors()

#snake_animation([Color.BLUE.value, Color.RED.value, Color.BLUE.value, Color.RED.value], length=20)

# light_sides({
#     "top": Color.BLUE,
#     "bottom": Color.BLUE,
#     "left": Color.RED,
#     "right": Color.RED
# })

while True:
    time.sleep(1)