import tkinter as tk
import subprocess
import os
import psutil
import time

# Automatically detect where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure it uses the piqueserver folder beside the EXE
PIQUESERVER_PATH = os.path.join(SCRIPT_DIR, "piqueserver")
CONFIG_PATH = os.path.join(PIQUESERVER_PATH, "config.toml")

# OpenSpades Config (Modify if needed)
OPENSPADES_PATH = r"E:\Games\OpenSpades-0.1.3-Windows\OpenSpades.exe"
SERVER_IP = "127.0.0.1"
SERVER_PORT = "8001"
PYTHON_EXEC = r"C:\Users\PERSONAL\AppData\Local\Programs\Python\Python310\python.exe"  # Adjust if needed

# Global variable for server process
server_process = None

# Function to check if the server is running
def is_server_running():
    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            if process.info['name'] and "python" in process.info['name'].lower():
                cmdline = " ".join(process.info['cmdline']) if process.info['cmdline'] else ""
                if "piqueserver" in cmdline:
                    print(f"Detected running server: PID {process.info['pid']}")  # Debugging
                    return process.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

# Function to start the server
def start_server():
    global server_process
    if is_server_running():
        status_label.config(text="Server is already running!", fg="blue")
        return True  # Return True if server is already running

    try:
        if not os.path.exists(CONFIG_PATH):
            status_label.config(text="Error: config.toml not found!", fg="red")
            print("Error: config.toml not found!")
            return False

        command = [PYTHON_EXEC, "-m", "piqueserver", "-c", CONFIG_PATH]
        print("Running Command:", " ".join(command))

        server_process = subprocess.Popen(
            command,  
            cwd=PIQUESERVER_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait and check multiple times for server to start
        for _ in range(10):  # Try for 10 seconds total
            time.sleep(1)
            if is_server_running():
                status_label.config(text="Server started successfully!", fg="green")
                print("✅ Server is running!")
                return True

        status_label.config(text="Server may have failed to start.", fg="red")
        print("❌ Server did NOT start.")
        return False

    except Exception as e:
        status_label.config(text=f"Failed to start server: {str(e)}", fg="red")
        print("Error:", str(e))
        return False

# Function to stop the server
def stop_server():
    server_pid = is_server_running()
    if server_pid:
        subprocess.run(["taskkill", "/F", "/PID", str(server_pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        status_label.config(text="Server stopped.", fg="red")
    else:
        status_label.config(text="No server running.", fg="blue")  # Avoids false errors

# Function to check if OpenSpades is running
def is_game_running():
    for process in psutil.process_iter(attrs=['name']):
        if "OpenSpades.exe" in process.info['name']:
            return True
    return False

# Function to launch OpenSpades and connect automatically
def launch_game():
    if not is_server_running():
        if not start_server():
            status_label.config(text="Failed to start server!", fg="red")
            return
        time.sleep(2)

    if is_game_running():
        status_label.config(text="Game already running!", fg="blue")
        return

    try:
        # Try multiple connection methods
        connection_methods = [
            f"spades://{SERVER_IP}:{SERVER_PORT}",  # Modern versions
            f"{SERVER_IP}:{SERVER_PORT}",            # Some intermediate versions
            ["--host", SERVER_IP, "--port", SERVER_PORT]  # Older versions
        ]

        for method in connection_methods:
            try:
                args = [OPENSPADES_PATH] + ([method] if isinstance(method, str) else method)
                subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
                status_label.config(text="Game launched!", fg="green")
                return
            except:
                continue

        status_label.config(text="Failed to launch game", fg="red")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")




# Function to handle window close
def on_close():
    stop_server()  # Ensure server stops when closing GUI
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("OpenSpades Offline Matchmaking")
root.geometry("300x300")

# Status Label
status_label = tk.Label(root, text="Status: Ready", fg="black")
status_label.pack(pady=5)

# Start Server Button
btn_start = tk.Button(root, text="Start Server", command=start_server, width=20)
btn_start.pack(pady=10)

# Stop Server Button
btn_stop = tk.Button(root, text="Stop Server", command=stop_server, width=20)
btn_stop.pack(pady=10)

# Launch OpenSpades Button
btn_launch = tk.Button(root, text="Start Game & Join", command=launch_game, width=20)
btn_launch.pack(pady=10)

# Close Window Event
root.protocol("WM_DELETE_WINDOW", on_close)

# Run the GUI
root.mainloop()
