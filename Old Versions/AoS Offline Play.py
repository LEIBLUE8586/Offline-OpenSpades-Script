import tkinter as tk
import subprocess
import os
import psutil
import time

# Paths (Modify these accordingly)
PIQUESERVER_PATH = r"D:\Personal Projects\Coding Project\Ace of Spades Offline Play\piqueserver"
OPENSPADES_PATH = r"E:\Games\OpenSpades-0.1.3-Windows\OpenSpades.exe"
CONFIG_PATH = os.path.join(PIQUESERVER_PATH, "config.toml")  # Piqueserver config file
SERVER_IP = "127.0.0.1"
SERVER_PORT = "8001"
PYTHON_EXEC = r"C:\Users\PERSONAL\AppData\Local\Programs\Python\Python310\python.exe"

# Global variable to track server process
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
        return

    try:
        CONFIG_FILE = r"D:\Personal Projects\Coding Project\Ace of Spades Offline Play\piqueserver\config.toml"

        if not os.path.exists(CONFIG_FILE):
            status_label.config(text="Error: config.toml not found!", fg="red")
            print("Error: config.toml not found!")
            return

        command = [PYTHON_EXEC, "-m", "piqueserver", "-c", CONFIG_FILE]

        print("Running Command:", " ".join(command))  # Debug Output

        server_process = subprocess.Popen(
            command,  
            cwd=PIQUESERVER_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 🔹 Wait 5 seconds before checking if server actually started
        time.sleep(5)  

        if is_server_running():
            status_label.config(text="Server started successfully!", fg="green")
            print("✅ Server is running!")
        else:
            status_label.config(text="Server may have failed to start.", fg="red")
            print("❌ Server did NOT start.")

    except Exception as e:
        status_label.config(text=f"Failed to start server: {str(e)}", fg="red")
        print("Error:", str(e))
        
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

# Function to launch OpenSpades
def launch_game():
    if not is_server_running():
        status_label.config(text="Start the server first!", fg="red")
        return
    
    if is_game_running():
        status_label.config(text="Game is already running!", fg="blue")
        return

    try:
        print(f"Launching OpenSpades and connecting to {SERVER_IP}:{SERVER_PORT}...")

        # ✅ Correct connection command
        subprocess.Popen([
            OPENSPADES_PATH,
            f"--host={SERVER_IP}",
            f"--port={SERVER_PORT}"
        ])

        status_label.config(text="Game launched and connecting...", fg="green")
    except Exception as e:
        status_label.config(text=f"Failed to launch game: {str(e)}", fg="red")
        print("Error:", str(e))


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