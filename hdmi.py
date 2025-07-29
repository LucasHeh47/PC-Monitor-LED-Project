import cv2
import random
import numpy as np

# Open capture card globally once
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open HDMI capture device")

sample_points = []

def init_sample_points(rows=5, cols=5):
    """Generate evenly spaced pixel positions across the screen."""
    global sample_points
    ret, frame = cap.read()
    if not ret:
        raise Exception("Failed to grab frame during init")

    height, width, _ = frame.shape
    y_spacing = height // (rows + 1)
    x_spacing = width // (cols + 1)

    sample_points = [
        (y_spacing * (r + 1), x_spacing * (c + 1))
        for r in range(rows)
        for c in range(cols)
    ]

def get_average_screen_color():
    if not sample_points:
        init_sample_points()

    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return (0, 0, 0)

    pixels = [frame[y, x] for y, x in sample_points]

    # Convert BGR to RGB
    rgb_pixels = [tuple(reversed(p)) for p in pixels]
    avg_color = tuple(int(np.mean([p[i] for p in rgb_pixels])) for i in range(3))
    return avg_color

# Optional: clean up
def release_capture():
    cap.release()
