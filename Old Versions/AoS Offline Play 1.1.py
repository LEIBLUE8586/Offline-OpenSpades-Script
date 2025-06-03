import tkinter as tk
from tkinter import ttk
import subprocess
import os
import psutil
import time
import webbrowser

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PIQUESERVER_PATH = os.path.join(SCRIPT_DIR, "piqueserver")
CONFIG_PATH = os.path.join(PIQUESERVER_PATH, "config.toml")
OPENSPADES_PATH = r"E:\Games\OpenSpades-0.1.3-Windows\OpenSpades.exe"
PYTHON_EXEC = r"C:\Users\PERSONAL\AppData\Local\Programs\Python\Python310\python.exe"

# Default values
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = "8001"

class OpenSpadesLauncher:
    def __init__(self, root):
        self.root = root
        self.server_process = None
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("OpenSpades Offline Launcher")
        self.root.geometry("400x400")
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Ready", fg="black")
        self.status_label.pack(pady=10)
        
        # Server Address Frame
        addr_frame = tk.Frame(self.root)
        addr_frame.pack(pady=10)
        
        tk.Label(addr_frame, text="Server IP:").grid(row=0, column=0, padx=5)
        self.ip_entry = tk.Entry(addr_frame, width=15)
        self.ip_entry.insert(0, DEFAULT_IP)
        self.ip_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(addr_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_entry = tk.Entry(addr_frame, width=8)
        self.port_entry.insert(0, DEFAULT_PORT)
        self.port_entry.grid(row=0, column=3, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        self.btn_start = tk.Button(btn_frame, text="Start Server", command=self.start_server, width=15)
        self.btn_start.grid(row=0, column=0, padx=5)
        
        self.btn_stop = tk.Button(btn_frame, text="Stop Server", command=self.stop_server, width=15)
        self.btn_stop.grid(row=0, column=1, padx=5)
        
        self.btn_launch = tk.Button(self.root, text="Launch OpenSpades", command=self.launch_game, width=20)
        self.btn_launch.pack(pady=10)
        
        self.btn_join = tk.Button(self.root, text="Join Server Only", command=self.join_server, width=20)
        self.btn_join.pack(pady=5)
        
        # Alternative Methods Label
        tk.Label(self.root, text="Alternative Connection Methods:").pack(pady=(20,5))
        
        # Alternative Methods Buttons
        alt_frame = tk.Frame(self.root)
        alt_frame.pack()
        
        self.btn_url = tk.Button(alt_frame, text="spades:// URL", command=self.launch_via_url, width=15)
        self.btn_url.grid(row=0, column=0, padx=5)
        
        self.btn_direct = tk.Button(alt_frame, text="Direct Connect", command=self.launch_direct_connect, width=15)
        self.btn_direct.grid(row=0, column=1, padx=5)
        
        # Console Output
        self.console = tk.Text(self.root, height=8, state='disabled')
        self.console.pack(pady=10, fill=tk.X)
        
        root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def log(self, message):
        self.console.config(state='normal')
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.config(state='disabled')
    
    def get_server_address(self):
        ip = self.ip_entry.get().strip() or DEFAULT_IP
        port = self.port_entry.get().strip() or DEFAULT_PORT
        return ip, port
    
    def is_server_running(self):
        for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
            try:
                if process.info['name'] and "python" in process.info['name'].lower():
                    cmdline = " ".join(process.info['cmdline']) if process.info['cmdline'] else ""
                    if "piqueserver" in cmdline:
                        self.log(f"Server running (PID: {process.info['pid']})")
                        return process.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_server(self):
        if self.is_server_running():
            self.status_label.config(text="Server already running!", fg="blue")
            self.log("Server already running")
            return True
            
        try:
            if not os.path.exists(CONFIG_PATH):
                self.status_label.config(text="config.toml not found!", fg="red")
                self.log("Error: config.toml not found!")
                return False

            command = [PYTHON_EXEC, "-m", "piqueserver", "-c", CONFIG_PATH]
            self.log(f"Starting server: {' '.join(command)}")

            self.server_process = subprocess.Popen(
                command,
                cwd=PIQUESERVER_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            for _ in range(10):
                time.sleep(1)
                if self.is_server_running():
                    ip, port = self.get_server_address()
                    self.status_label.config(text=f"Server running at {ip}:{port}", fg="green")
                    self.log("Server started successfully")
                    return True

            self.status_label.config(text="Server failed to start", fg="red")
            self.log("Server failed to start after 10 seconds")
            return False
            
        except Exception as e:
            self.status_label.config(text=f"Server error: {str(e)}", fg="red")
            self.log(f"Error starting server: {str(e)}")
            return False
    
    def stop_server(self):
        server_pid = self.is_server_running()
        if server_pid:
            subprocess.run(["taskkill", "/F", "/PID", str(server_pid)], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            self.status_label.config(text="Server stopped", fg="red")
            self.log("Server stopped")
        else:
            self.status_label.config(text="No server running", fg="blue")
            self.log("No server running to stop")
    
    def is_game_running(self):
        for process in psutil.process_iter(attrs=['name']):
            if process.info['name'] and "OpenSpades.exe" in process.info['name']:
                return True
        return False
    
    def launch_game(self):
        """Main method to launch game and connect to server"""
        if not self.is_server_running():
            if not self.start_server():
                return
            time.sleep(2)
        
        if self.is_game_running():
            self.status_label.config(text="Game already running", fg="blue")
            self.log("OpenSpades already running")
            return
        
        ip, port = self.get_server_address()
        self.log(f"Attempting to launch OpenSpades and connect to {ip}:{port}")
        
        # Try multiple connection methods
        methods = [
            self.launch_via_url,
            self.launch_direct_connect,
            self.launch_old_method
        ]
        
        for method in methods:
            try:
                method()
                return
            except Exception as e:
                self.log(f"Connection method failed: {str(e)}")
                continue
        
        self.status_label.config(text="All connection methods failed", fg="red")
        self.log("All connection attempts failed")
    
    def join_server(self):
        """Just connect to an existing server without starting one"""
        if self.is_game_running():
            self.status_label.config(text="Game already running", fg="blue")
            return
        
        ip, port = self.get_server_address()
        self.log(f"Attempting to connect to {ip}:{port}")
        self.launch_via_url()
    
    def launch_via_url(self):
        """Modern spades:// URL method"""
        ip, port = self.get_server_address()
        url = f"spades://{ip}:{port}"
        self.log(f"Trying spades:// URL method: {url}")
        
        try:
            # Try using webbrowser first
            webbrowser.open(url)
            self.status_label.config(text="Launched via spades:// URL", fg="green")
            self.log("Opened spades:// URL successfully")
            return
        except:
            pass
        
        # Fallback to direct executable call
        try:
            subprocess.Popen([OPENSPADES_PATH, url], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.status_label.config(text="Game launched via URL", fg="green")
            self.log("Launched OpenSpades with URL parameter")
        except Exception as e:
            raise Exception(f"URL method failed: {str(e)}")
    
    def launch_direct_connect(self):
        """Direct IP:PORT connection method"""
        ip, port = self.get_server_address()
        address = f"{ip}:{port}"
        self.log(f"Trying direct connection: {address}")
        
        try:
            subprocess.Popen([OPENSPADES_PATH, address], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.status_label.config(text="Game launched directly", fg="green")
            self.log("Launched with direct address")
        except Exception as e:
            raise Exception(f"Direct connect failed: {str(e)}")
    
    def launch_old_method(self):
        """Legacy --host and --port method"""
        ip, port = self.get_server_address()
        self.log(f"Trying legacy connection: --host {ip} --port {port}")
        
        try:
            subprocess.Popen(
                [OPENSPADES_PATH, "--host", ip, "--port", port],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.status_label.config(text="Game launched (legacy method)", fg="green")
            self.log("Launched with legacy parameters")
        except Exception as e:
            raise Exception(f"Legacy method failed: {str(e)}")
    
    def on_close(self):
        self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenSpadesLauncher(root)
    root.mainloop()