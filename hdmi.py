import cv2
import random
import numpy as np

# Open capture card globally once
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open HDMI capture device")

def get_average_screen_color(sample_count=50, spread=50):
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return (0, 0, 0)

    height, width, _ = frame.shape

    # Random center point
    center_y = random.randint(spread, height - spread - 1)
    center_x = random.randint(spread, width - spread - 1)

    pixels = []
    for _ in range(sample_count):
        dy = random.randint(-spread, spread)
        dx = random.randint(-spread, spread)
        y = min(max(center_y + dy, 0), height - 1)
        x = min(max(center_x + dx, 0), width - 1)
        pixels.append(frame[y, x])

    # Convert from BGR to RGB and average
    rgb_pixels = [tuple(reversed(p)) for p in pixels]
    avg_color = tuple(int(np.mean([p[i] for p in rgb_pixels])) for i in range(3))

    return avg_color

# Optional: clean up
def release_capture():
    cap.release()
