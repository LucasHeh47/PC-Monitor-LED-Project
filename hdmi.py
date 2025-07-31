import cv2
import random
import numpy as np

# Open capture card globally once
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open HDMI capture device")

sample_points = []

def get_average_screen_color_fast():
    ret, frame = cap.read()
    avg_color = cv2.resize(frame, (1, 1), interpolation=cv2.INTER_AREA)
    # Extract RGB tuple (OpenCV is BGR by default)
    b, g, r = avg_color[0, 0]
    return int(r), int(g), int(b)



# Optional: clean up
def release_capture():
    cap.release()
