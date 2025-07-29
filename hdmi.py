import cv2
import random
import numpy as np

# Open capture card globally once
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open HDMI capture device")

def get_average_screen_color(num_samples=100, max_offset=50):
    cap = cv2.VideoCapture(0)  # Use the correct index for your HDMI capture
    if not cap.isOpened():
        print("Cannot open HDMI capture device")
        return (0, 0, 0)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to grab frame")
        return (0, 0, 0)

    h, w, _ = frame.shape
    total_color = np.array([0, 0, 0], dtype=np.uint64)
    count = 0

    for _ in range(num_samples):
        x = random.randint(max_offset, w - max_offset - 1)
        y = random.randint(max_offset, h - max_offset - 1)

        # Include center pixel
        total_color += frame[y, x]
        count += 1

        # Check pixels at offsets up/down/left/right up to max_offset
        for offset in range(1, max_offset + 1, 10):  # step by 10 pixels to keep it efficient
            positions = [
                (x + offset, y),
                (x - offset, y),
                (x, y + offset),
                (x, y - offset),
            ]
            for px, py in positions:
                if 0 <= px < w and 0 <= py < h:
                    total_color += frame[py, px]
                    count += 1

    avg_color = (total_color / count).astype(int)
    return tuple(avg_color[::-1])  # BGR to RGB

# Optional: clean up
def release_capture():
    cap.release()
