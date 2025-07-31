import socket
import json
from tkinter import colorchooser
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import paramiko
from color import Color
import os

version = "1.1"

HOST = "10.0.55.50"
PORT = 8888

Color.load_custom_colors()

def run_ssh_command(command):
    ssh_host = HOST         # e.g., "10.0.55.50"
    ssh_port = 22           # SSH usually runs on port 22, not 8888
    ssh_user = os.getenv("LED_NAME")
    print(os.getenv("LED_NAME"))
    ssh_password = os.getenv("LED_KEY")  # <-- or set up key authentication
    print("Executing " + command)
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)

        stdin, stdout, stderr = client.exec_command("sudo " + command)

        stdin.write(os.getenv("LED_KEY\n"))
        stdin.flush()

        output = stdout.read().decode()
        error = stderr.read().decode()

        client.close()

        if error:
            return f"[stderr]\n{error.strip()}"
        return output.strip()

    except Exception as e:
        return f"[error] {str(e)}"

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

        # Send to Pi
        send_json({"add_color": name, "r": r, "g": g, "b": b})



def update_color_dropdown():
    available_colors['values'] = [c.lower() for c in Color.all().keys()]


# --- GUI Setup ---
app = ttk.Window(f"LED Controller v{version}", themename="cosmo", size=(800, 1000))
app.place_window_center()


ttk.Label(app, text="LED Light Controller", font=("Arial", 24, "bold")).pack(pady=12)

toggle_var = tk.BooleanVar(value=True)

toggle_frame = ttk.Frame(app)
toggle_frame.pack(pady=10)

# Toggle on/off
def on_toggle():
    if toggle_var.get():
        data = {
            "animation": "solid",
            "colors": ["BLUE"],
            "speed": 0.01
        }
        send_json(data)
    else:
        data = {
            "animation": "solid",
            "colors": ["BLACK"],
            "speed": 0.01
        }
        send_json(data)

ttk.Checkbutton(
    toggle_frame,
    variable=toggle_var,
    bootstyle="round-toggle-button",
    text="Power",
    command=on_toggle
).pack(side="left", padx=5)

# Restart button
ttk.Button(app, text="Restart LEDs", style="danger", command=lambda: run_ssh_command("systemctl restart led-program")).pack(pady=5)


# --- Animation Type Options ---
ttk.Label(app, text="Animation Type").pack(pady=5)

animation = tk.StringVar(value="solid")

anim_frame = ttk.Frame(app)
anim_frame.pack(padx=10, pady=5)

anim_options = ["solid", "breathing", "snake", "rainbow", "average_screen_color"]

# Get the longest text label (pretty title)
longest_label = max(anim_options, key=lambda s: len(s.replace("_", " ").title()))
char_width = len(longest_label.replace("_", " ").title()) + 2  # +2 for padding

# Layout: 2 columns
cols = 2
for i, anim_type in enumerate(anim_options):
    row = i // cols
    col = i % cols

    # Center last item if count is odd and it's the final one
    colspan = 1
    sticky = "nsew"
    if len(anim_options) % 2 == 1 and i == len(anim_options) - 1:
        col = 0
        colspan = 2
        sticky = ""

    rb = ttk.Radiobutton(
        anim_frame,
        text=anim_type.replace("_", " ").title(),
        value=anim_type,
        variable=animation,
        style="Toolbutton"
    )
    rb.grid(row=row, column=col, columnspan=colspan, padx=8, pady=8, sticky=sticky)
    rb.configure(width=char_width)  # Width in characters

print(animation.get())
if animation.get() not in ["rainbow", "average_screen_color"]:

    # --- Available Colors ---
    ttk.Label(app, text="Available Colors").pack(pady=5)

    color_buttons_frame = ttk.Frame(app)
    color_buttons_frame.pack(padx=10, pady=5)

    available_colors = tk.StringVar(value="blue")

    color_list = [c.lower() for c in Color.all()]

    # Get longest color name (visually)
    longest_name = max(color_list, key=len)
    char_width = len(longest_name) + 2  # Add a little padding

    cols = 6
    style = ttk.Style()
    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)
    for i, color in enumerate(color_list):
        style_name = f"{color}.Toolbutton"
        hex_color = rgb_to_hex(Color.get(color).value)

        r, g, b = Color.get(color).value
        brightness = (r * 299 + g * 587 + b * 114) / 1000  # standard luminance formula

        if brightness > 128:
            fg_color = "black"
        else:
            fg_color = "white"

        style.configure(style_name, background=hex_color, foreground=fg_color)
        style.map(style_name, background=[('active', hex_color)])

        row = i // cols
        col = i % cols

        # Handle odd number last-row centering (optional)
        if i == len(color_list) - 1 and len(color_list) % cols != 0 and col == 0:
            # Center the last button across 4 cols
            colspan = cols
        else:
            colspan = 1

        ttk.Radiobutton(
            color_buttons_frame,
            text=color.title(),
            value=color,
            style = style_name,
            variable=available_colors
        ).grid(
            row=row,
            column=col,
            columnspan=colspan,
            padx=5,
            pady=5,
            sticky="nsew"
        )



    ttk.Button(app, text="➕ Add Color", bootstyle="success", command=add_color).pack(pady=5)

    ttk.Label(app, text="Used Colors (Drag Order / Select to Remove)").pack(pady=5)
    used_colorsbox = tk.Listbox(app, selectmode=tk.MULTIPLE, height=6, width=50, bg="white")
    used_colorsbox.pack()

    ttk.Button(app, text="❌ Remove Selected", bootstyle="danger", command=remove_color).pack(pady=5)

    ttk.Label(app, text="Speed (float)").pack(pady=5)
    speed_entry = ttk.Entry(app)
    speed_entry.insert(0, "0.05")
    speed_entry.pack(padx=20)

    ttk.Label(app, text="Length (int, for snake)").pack(pady=5)
    length_entry = ttk.Entry(app)
    length_entry.insert(0, "10")
    length_entry.pack(padx=20)

# --- Custom Color Creator ---
ttk.Label(app, text="Create Custom Color").pack(pady=10)
custom_name_entry = ttk.Entry(app)
custom_name_entry.pack(padx=20, pady=5)

ttk.Button(app, text="🎨 Pick & Add Custom Color", bootstyle="info", command=create_custom_color).pack(pady=5)

ttk.Button(app, text="🚀 Send to LED Strip", bootstyle="primary", command=submit).pack(pady=20)

app.mainloop()
