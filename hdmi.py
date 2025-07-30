import cv2
import random
import numpy as np

# Open capture card globally once
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open HDMI capture device")

sample_points = []

def init_sample_points(sample_count=150):
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


def sample_triangle_pixels(frame, led_pos, center, num_samples=40, offset=20):
    """
    Samples a triangle area between LED and center using barycentric coordinates.
    Each sample includes surrounding pixels.
    """
    height, width, _ = frame.shape
    pixels = []

    for _ in range(num_samples):
        t = random.random()
        u = random.random() * (1 - t)
        v = 1 - t - u

        # Barycentric interpolation for triangle between led, center, and midpoint
        x = int(t * center[0] + u * led_pos[0] + v * ((led_pos[0] + center[0]) // 2))
        y = int(t * center[1] + u * led_pos[1] + v * ((led_pos[1] + center[1]) // 2))

        if 0 <= x < width and 0 <= y < height:
            pixels.append(frame[y, x])

            # Add surrounding pixels
            for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
                sx, sy = x + dx, y + dy
                if 0 <= sx < width and 0 <= sy < height:
                    pixels.append(frame[sy, sx])

    return pixels

def get_all_led_colors_from_map(frame, led_sample_map):
    height, width, _ = frame.shape
    all_colors = []

    for samples in led_sample_map:
        valid_pixels = [
            frame[y, x] for x, y in samples
            if 0 <= x < width and 0 <= y < height
        ]

        if valid_pixels:
            rgb_pixels = [tuple(reversed(p)) for p in valid_pixels]
            avg_color = tuple(int(np.mean([p[i] for p in rgb_pixels])) for i in range(3))
        else:
            avg_color = (0, 0, 0)

        all_colors.append(avg_color)

    return all_colors





# Optional: clean up
def release_capture():
    cap.release()
