import threading
import socket
import json
from program import handle_JSON

def json_listener_thread(port=8888):
    global animating

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(1)
    print(f"Listening for JSON on port {port}...")

    while True:
        client, addr = server.accept()
        data = client.recv(1024).decode()
        try:
            json_data = json.loads(data)
            handle_JSON(json_data)
        except json.JSONDecodeError:
            print("Received invalid JSON")
        client.close()