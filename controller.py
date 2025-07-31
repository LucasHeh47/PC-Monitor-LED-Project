import socket
import json
from tkinter import colorchooser
import tkinter as tk
import ttkbootstrap as ttk

from color import Color
import os

version = "1.1"

HOST = "10.0.55.50"
PORT = 8888

Color.load_custom_colors()

def send_json(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(data).encode('utf-8'))
            s.shutdown(socket.SHUT_WR)
    except Exception as e:
        print("Error:", e)

def submit():
    anim = animation.get()
    colors = [used_colorsbox.get(i) for i in range(used_colorsbox.size())]
    speed_val = speed_entry.get()
    length_val = length_entry.get()

    try:
        speed = float(speed_val)
    except ValueError:
        speed = 0.05

    try:
        length = int(length_val)
    except ValueError:
        length = 10

    data = {
        "animation": anim,
        "colors": [c.lower() for c in colors],
        "speed": speed
    }
    if anim == "snake":
        data["length"] = length

    send_json(data)

def add_color():
    selection = available_colors.get()
    if selection:
        used_colorsbox.insert(tk.END, selection)

def remove_color():
    selected = used_colorsbox.curselection()
    for i in reversed(selected):
        used_colorsbox.delete(i)

def create_custom_color():
    name = custom_name_entry.get().strip().lower()
    if not name:
        return

    rgb, _ = colorchooser.askcolor(title="Pick a custom color")
    if rgb:
        r, g, b = map(int, rgb)
        Color.add_custom_color(name, r, g, b)
        update_color_dropdown()
        available_colors.set(name)
        data = {
            "add_color": name,
            "r": r,
            "g": g,
            "b": b
        }
        send_json(data)

def update_color_dropdown():
    available_colors['values'] = [c.lower() for c in Color.all().keys()]


# --- GUI Setup ---
app = ttk.Window(f"LED Controller v{version}", themename="cosmo", size=(500, 650))
app.place_window_center()

ttk.Label(app, text="Animation Type").pack(pady=5)
animation = ttk.Combobox(app, values=["solid", "breathing", "snake", "average_screen_color", "rainbow"])
animation.set("solid")
animation.pack(fill=tk.X, padx=20)

ttk.Label(app, text="Available Colors").pack(pady=5)
available_colors = ttk.Combobox(app, values=[c.lower() for c in Color.all()])
available_colors.set("blue")
available_colors.pack(fill=tk.X, padx=20)

ttk.Button(app, text="➕ Add Color", bootstyle="success", command=add_color).pack(pady=5)

ttk.Label(app, text="Used Colors (Drag Order / Select to Remove)").pack(pady=5)
used_colorsbox = tk.Listbox(app, selectmode=tk.MULTIPLE, height=6, bg="white")
used_colorsbox.pack(fill=tk.X, padx=20)

ttk.Button(app, text="❌ Remove Selected", bootstyle="danger", command=remove_color).pack(pady=5)

ttk.Label(app, text="Speed (float)").pack(pady=5)
speed_entry = ttk.Entry(app)
speed_entry.insert(0, "0.05")
speed_entry.pack(fill=tk.X, padx=20)

ttk.Label(app, text="Length (int, for snake)").pack(pady=5)
length_entry = ttk.Entry(app)
length_entry.insert(0, "10")
length_entry.pack(fill=tk.X, padx=20)

# --- Custom Color Creator ---
ttk.Label(app, text="Create Custom Color").pack(pady=10)
custom_name_entry = ttk.Entry(app)
custom_name_entry.pack(fill=tk.X, padx=20, pady=5)

ttk.Button(app, text="🎨 Pick & Add Custom Color", bootstyle="info", command=create_custom_color).pack(pady=5)

ttk.Button(app, text="🚀 Send to LED Strip", bootstyle="primary", command=submit).pack(pady=20)

app.mainloop()
