# MIT License
# Copyright (c) 2025 LEIBLUE 8586
"""
Offline Openspades Script by Nofal (Alias, Leiblue8586)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import psutil 
import time
import webbrowser
import json

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "launcher_config.json")
PIQUESERVER_PATH = os.path.join(SCRIPT_DIR, "piqueserver")
CONFIG_PATH = os.path.join(PIQUESERVER_PATH, "config.toml")
PYTHON_EXEC = r"C:\Users\PERSONAL\AppData\Local\Programs\Python\Python310\python.exe"

# Default values
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = "8001"
DEFAULT_OPENSPADES_PATH = ""
DEFAULT_BOT_SETTINGS = {
    "BOT_IN_BOTH": True,
    "BOT_ADD_PATTERN": 0,
    "BOT_ADD_NUM": 4,
    "LITE_MODE": False,
    "LV_AUTO_ADJUST": 0,
    "BOT_NUM_NAME": True,
    "CPU_LV": [50, 20],
    "BOTMUTE": False,
    "AI_mode": 0
}

class BotSettingsWindow:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("ABBS Bot Settings")
        self.window.geometry("400x500")
        
        # Initialize with config values
        self.bot_settings = self.config.get("bot_settings", DEFAULT_BOT_SETTINGS.copy())
        
        # Main frame with scrollbar
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bot Settings
        tk.Label(scrollable_frame, text="ABBS Bot Configuration", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Bots in both teams
        self.bot_in_both_var = tk.BooleanVar(value=self.bot_settings["BOT_IN_BOTH"])
        tk.Checkbutton(scrollable_frame, text="Bots in both teams", variable=self.bot_in_both_var).pack(anchor='w', pady=5)
        
        # Bot add pattern
        tk.Label(scrollable_frame, text="Bot Add Pattern:").pack(anchor='w', pady=(10,0))
        self.bot_add_pattern_var = tk.IntVar(value=self.bot_settings["BOT_ADD_PATTERN"])
        patterns = [("Evenly", 0), ("All to losing team", 1), ("All to winning team", 2), ("Random", 3)]
        for text, val in patterns:
            tk.Radiobutton(scrollable_frame, text=text, variable=self.bot_add_pattern_var, value=val).pack(anchor='w')
        
        # Number of bots
        tk.Label(scrollable_frame, text="Number of Bots:").pack(anchor='w', pady=(10,0))
        self.bot_add_num_var = tk.IntVar(value=self.bot_settings["BOT_ADD_NUM"])
        tk.Scale(scrollable_frame, from_=0, to=32, orient=tk.HORIZONTAL, variable=self.bot_add_num_var).pack(fill='x')
        
        # Lite mode
        self.lite_mode_var = tk.BooleanVar(value=self.bot_settings["LITE_MODE"])
        tk.Checkbutton(scrollable_frame, text="Lite Mode (simplified calculations)", variable=self.lite_mode_var).pack(anchor='w', pady=5)
        
        # Level auto adjust
        tk.Label(scrollable_frame, text="Auto Level Adjustment:").pack(anchor='w', pady=(10,0))
        self.lv_auto_adjust_var = tk.IntVar(value=self.bot_settings["LV_AUTO_ADJUST"])
        adjustments = [("None", 0), ("Easy", 1), ("Medium", 2), ("Hard", 3)]
        for text, val in adjustments:
            tk.Radiobutton(scrollable_frame, text=text, variable=self.lv_auto_adjust_var, value=val).pack(anchor='w')
        
        # Numbered bot names
        self.bot_num_name_var = tk.BooleanVar(value=self.bot_settings["BOT_NUM_NAME"])
        tk.Checkbutton(scrollable_frame, text="Numbered Bot Names", variable=self.bot_num_name_var).pack(anchor='w', pady=5)
        
        # Bot difficulty
        tk.Label(scrollable_frame, text="Bot Difficulty (Mean/Variation):").pack(anchor='w', pady=(10,0))
        cpu_frame = tk.Frame(scrollable_frame)
        cpu_frame.pack(fill='x')
        tk.Label(cpu_frame, text="Mean:").pack(side='left')
        self.cpu_lv_mean_var = tk.IntVar(value=self.bot_settings["CPU_LV"][0])
        tk.Scale(cpu_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.cpu_lv_mean_var).pack(side='left', fill='x', expand=True)
        
        cpu_frame2 = tk.Frame(scrollable_frame)
        cpu_frame2.pack(fill='x')
        tk.Label(cpu_frame2, text="Variation:").pack(side='left')
        self.cpu_lv_var_var = tk.IntVar(value=self.bot_settings["CPU_LV"][1])
        tk.Scale(cpu_frame2, from_=0, to=50, orient=tk.HORIZONTAL, variable=self.cpu_lv_var_var).pack(side='left', fill='x', expand=True)
        
        # Bot mute
        self.botmute_var = tk.BooleanVar(value=self.bot_settings["BOTMUTE"])
        tk.Checkbutton(scrollable_frame, text="Mute Bot Chat", variable=self.botmute_var).pack(anchor='w', pady=5)
        
        # AI Mode
        tk.Label(scrollable_frame, text="Game Mode:").pack(anchor='w', pady=(10,0))
        self.ai_mode_var = tk.IntVar(value=self.bot_settings["AI_mode"])
        modes = [
            ("TOW", 0), ("TDM", 1), ("Arena", 2), 
            ("vsBOT(all)", 3), ("vsBOT(alone)", 4), 
            ("vsBOT(intel)", 5), ("DOMINE", 6), ("kabadi", 7)
        ]
        for text, val in modes:
            tk.Radiobutton(scrollable_frame, text=text, variable=self.ai_mode_var, value=val).pack(anchor='w')
        
        # Save Button
        tk.Button(scrollable_frame, text="Save Settings", command=self.save_settings).pack(pady=20)
    
    def save_settings(self):
        self.bot_settings = {
            "BOT_IN_BOTH": self.bot_in_both_var.get(),
            "BOT_ADD_PATTERN": self.bot_add_pattern_var.get(),
            "BOT_ADD_NUM": self.bot_add_num_var.get(),
            "LITE_MODE": self.lite_mode_var.get(),
            "LV_AUTO_ADJUST": self.lv_auto_adjust_var.get(),
            "BOT_NUM_NAME": self.bot_num_name_var.get(),
            "CPU_LV": [self.cpu_lv_mean_var.get(), self.cpu_lv_var_var.get()],
            "BOTMUTE": self.botmute_var.get(),
            "AI_mode": self.ai_mode_var.get()
        }
        self.config["bot_settings"] = self.bot_settings
        self.window.destroy()

class OpenSpadesLauncher:
    def __init__(self, root):
        self.root = root
        self.server_process = None
        # Initialize config with default values
        self.config = {
            "openspades_path": DEFAULT_OPENSPADES_PATH,
            "server_ip": DEFAULT_IP,
            "server_port": DEFAULT_PORT,
            "bot_settings": DEFAULT_BOT_SETTINGS.copy()  # Make sure to use copy()
        }
        self.load_config()  # Load saved config
        self.setup_ui()
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    # Safely update each config value
                    for key in self.config:
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
                
                    # Ensure bot_settings has all required keys
                    if "bot_settings" in loaded_config:
                        for key in DEFAULT_BOT_SETTINGS:
                            if key not in loaded_config["bot_settings"]:
                                # If key is missing, use default value
                                loaded_config["bot_settings"][key] = DEFAULT_BOT_SETTINGS[key]
                        self.config["bot_settings"] = loaded_config["bot_settings"]
        except Exception as e:
            print(f"Error loading config: {e}")
            # If loading fails, use default config
            self.config["bot_settings"] = DEFAULT_BOT_SETTINGS.copy()
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            # Ensure all bot settings are included
            current_bot_settings = self.config.get("bot_settings", DEFAULT_BOT_SETTINGS.copy())
            for key in DEFAULT_BOT_SETTINGS:
                if key not in current_bot_settings:
                    current_bot_settings[key] = DEFAULT_BOT_SETTINGS[key]
        
            # Update config with current UI values
            current_config = {
                "openspades_path": self.path_entry.get().strip(),
                "server_ip": self.ip_entry.get().strip(),
                "server_port": self.port_entry.get().strip(),
                "bot_settings": current_bot_settings
            }
        
            # Merge with existing config
            self.config.update(current_config)
        
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        self.root.title("OpenSpades Offline Launcher")
        self.root.geometry("500x550")
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Ready", fg="black")
        self.status_label.pack(pady=10)
        
        # OpenSpades Path Frame
        path_frame = tk.Frame(self.root)
        path_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Label(path_frame, text="OpenSpades Path:").pack(side=tk.LEFT)
        self.path_entry = tk.Entry(path_frame)
        self.path_entry.insert(0, self.config["openspades_path"])
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.browse_btn = tk.Button(path_frame, text="Browse", command=self.browse_path)
        self.browse_btn.pack(side=tk.RIGHT)
        
        # Server Address Frame
        addr_frame = tk.Frame(self.root)
        addr_frame.pack(pady=10)
        
        tk.Label(addr_frame, text="Server IP:").grid(row=0, column=0, padx=5)
        self.ip_entry = tk.Entry(addr_frame, width=15)
        self.ip_entry.insert(0, self.config["server_ip"])
        self.ip_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(addr_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_entry = tk.Entry(addr_frame, width=8)
        self.port_entry.insert(0, self.config["server_port"])
        self.port_entry.grid(row=0, column=3, padx=5)
        
        # ABBS Bot Settings Button
        self.bot_settings_btn = tk.Button(self.root, text="ABBS Bot Settings", command=self.open_bot_settings)
        self.bot_settings_btn.pack(pady=5)
        
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
        self.console.pack(pady=10, fill=tk.X, padx=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def open_bot_settings(self):
        """Open the ABBS bot settings window"""
        bot_window = BotSettingsWindow(self.root, self.config)
        self.root.wait_window(bot_window.window)
        self.save_config()
        messagebox.showinfo("Settings Saved", "ABBS bot settings have been saved to config.")
    
    def browse_path(self):
        """Open file dialog to select OpenSpades executable"""
        initial_dir = os.path.expanduser("~")
        if os.path.exists("E:\\Games"):
            initial_dir = "E:\\Games"
        
        # Start from current path if one exists
        current_path = self.path_entry.get().strip()
        if current_path and os.path.exists(os.path.dirname(current_path)):
            initial_dir = os.path.dirname(current_path)
            
        file_path = filedialog.askopenfilename(
            title="Select OpenSpades executable",
            initialdir=initial_dir,
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
            self.log(f"Set OpenSpades path to: {file_path}")
            self.save_config()  # Save when path changes
    
    def get_openspades_path(self):
        """Get the OpenSpades path from entry or return None if invalid"""
        path = self.path_entry.get().strip()
        if not path:
            self.log("Error: OpenSpades path not set!")
            self.status_label.config(text="Error: OpenSpades path not set!", fg="red")
            return None
            
        if not os.path.exists(path):
            self.log(f"Error: Path does not exist: {path}")
            self.status_label.config(text="Error: Invalid OpenSpades path!", fg="red")
            return None
            
        return path
    
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
        
        openspades_path = self.get_openspades_path()
        if not openspades_path:
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
        
        openspades_path = self.get_openspades_path()
        if not openspades_path:
            return
            
        ip, port = self.get_server_address()
        self.log(f"Attempting to connect to {ip}:{port}")
        self.launch_via_url()
    
    def launch_via_url(self):
        """Modern spades:// URL method"""
        openspades_path = self.get_openspades_path()
        if not openspades_path:
            return
            
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
            subprocess.Popen([openspades_path, url], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.status_label.config(text="Game launched via URL", fg="green")
            self.log("Launched OpenSpades with URL parameter")
        except Exception as e:
            raise Exception(f"URL method failed: {str(e)}")
    
    def launch_direct_connect(self):
        """Direct IP:PORT connection method"""
        openspades_path = self.get_openspades_path()
        if not openspades_path:
            return
            
        ip, port = self.get_server_address()
        address = f"{ip}:{port}"
        self.log(f"Trying direct connection: {address}")
        
        try:
            subprocess.Popen([openspades_path, address], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.status_label.config(text="Game launched directly", fg="green")
            self.log("Launched with direct address")
        except Exception as e:
            raise Exception(f"Direct connect failed: {str(e)}")
    
    def launch_old_method(self):
        """Legacy --host and --port method"""
        openspades_path = self.get_openspades_path()
        if not openspades_path:
            return
            
        ip, port = self.get_server_address()
        self.log(f"Trying legacy connection: --host {ip} --port {port}")
        
        try:
            subprocess.Popen(
                [openspades_path, "--host", ip, "--port", port],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.status_label.config(text="Game launched (legacy method)", fg="green")
            self.log("Launched with legacy parameters")
        except Exception as e:
            raise Exception(f"Legacy method failed: {str(e)}")
    
    def on_close(self):
        self.save_config()  # Save before closing
        self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenSpadesLauncher(root)
    root.mainloop()