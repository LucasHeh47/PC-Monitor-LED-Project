import cv2
import random
import numpy as np

# Open capture card globally once
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open HDMI capture device")

sample_points = []

def init_sample_points(sample_count=50):
    """Initialize evenly spaced sample points based on desired count."""
    global sample_points
    ret, frame = cap.read()
    if not ret:
        raise Exception("Failed to grab frame during init")

    height, width, _ = frame.shape

    # Compute square grid size closest to sample_count
    grid_size = int(np.ceil(np.sqrt(sample_count)))
    x_spacing = width // (grid_size + 1)
    y_spacing = height // (grid_size + 1)

    points = []
    for row in range(grid_size):
        for col in range(grid_size):
            if len(points) >= sample_count:
                break
            x = (col + 1) * x_spacing
            y = (row + 1) * y_spacing
            points.append((y, x))

    sample_points = points

def get_average_screen_color(offset=20):
    if not sample_points:
        init_sample_points()

    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return (0, 0, 0)

    height, width, _ = frame.shape
    collected_pixels = []

    for y, x in sample_points:
        # Center
        if 0 <= y < height and 0 <= x < width:
            collected_pixels.append(frame[y, x])

        # Up
        if y - offset >= 0:
            collected_pixels.append(frame[y - offset, x])
        # Down
        if y + offset < height:
            collected_pixels.append(frame[y + offset, x])
        # Left
        if x - offset >= 0:
            collected_pixels.append(frame[y, x - offset])
        # Right
        if x + offset < width:
            collected_pixels.append(frame[y, x + offset])

    if not collected_pixels:
        return (0, 0, 0)

    # Convert BGR to RGB and average
    rgb_pixels = [tuple(reversed(p)) for p in collected_pixels]
    avg_color = tuple(int(np.mean([p[i] for p in rgb_pixels])) for i in range(3))
    return avg_color


# Optional: clean up
def release_capture():
    cap.release()
