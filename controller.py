import socket
import json
from enum import Enum

class Color(Enum):
    RED     = (255, 0, 0)
    GREEN   = (0, 255, 0)
    BLUE    = (0, 0, 255)
    WHITE   = (255, 255, 255)
    BLACK   = (0, 0, 0)
    YELLOW  = (255, 255, 0)
    CYAN    = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE  = (255, 80, 0)
    PURPLE  = (128, 0, 128)
    VIOLET  = (128, 0, 255)
    PINK    = (255, 105, 180)
    TEAL    = (0, 128, 128)

HOST = "10.0.55.50"
PORT = 8888

data = {
    "animation": "average_screen_color",
    "colors": ["blue", "red", "green", "yellow"],
    "speed": 0.005,
    "length": 5
}

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(data).encode('utf-8'))
        s.shutdown(socket.SHUT_WR)  # Tell the server we're done sending

if __name__ == "__main__":
    main()
