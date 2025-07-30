import socket
import json

HOST = "10.0.55.50"
PORT = 8888

data = {
    "animation": "solid",
    "colors": ["blue"]
}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(json.dumps(data).encode('utf-8'))
    s.shutdown(socket.SHUT_WR)  # Tell the server we're done sending
