import socket
import json

HOST = "10.0.55.50"
PORT = 8888

data = {
    "animation": "solid",
    "colors": ["blue"]
}

json_str = json.dumps(data)
http_request = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Content-Type: application/json\r\n"
    f"Content-Length: {len(json_str)}\r\n"
    f"\r\n"
    f"{json_str}"
)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(http_request.encode())
