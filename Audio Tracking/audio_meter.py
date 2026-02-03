import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pyaudio
import numpy as np
import threading
import time

class AudioMeterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Meter")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # Audio Configuration
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False
        
        # GUI Setup
        self.setup_ui()
        
        # Populate devices
        self.populate_devices()
        
    def setup_ui(self):
        # styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#333333")
        style.configure("TLabel", background="#333333", foreground="#ffffff")
        style.configure("TButton", background="#555555", foreground="#ffffff", borderwidth=1)
        style.map("TButton", background=[("active", "#777777")])
        
        self.root.configure(bg="#333333")
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Device Selection
        lbl_device = ttk.Label(main_frame, text="Select Audio Device:")
        lbl_device.pack(anchor=tk.W, pady=(0, 5))
        
        self.device_var = tk.StringVar()
        self.combo_devices = ttk.Combobox(main_frame, textvariable=self.device_var, state="readonly")
        self.combo_devices.pack(fill=tk.X, pady=(0, 20))
        self.combo_devices.bind("<<ComboboxSelected>>", self.on_device_change)
        
        # Meter Container
        self.canvas_width = 100
        self.canvas_height = 400
        self.meter_canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height, bg="#2b2b2b", highlightthickness=0)
        self.meter_canvas.pack(pady=10)
        
        # Draw static meter background (gradient blocks simulation)
        self.draw_meter_background()
        
        # The active bar (initially empty)
        self.meter_bar = self.meter_canvas.create_rectangle(0, self.canvas_height, self.canvas_width, self.canvas_height, fill="green", outline="")
        
        # Text display for dB
        self.lbl_db = ttk.Label(main_frame, text="- inf dB", font=("Helvetica", 24))
        self.lbl_db.pack(pady=20)
        
        # Control Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start = ttk.Button(btn_frame, text="Start Monitoring", command=self.start_monitoring)
        self.btn_start.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.btn_stop = ttk.Button(btn_frame, text="Stop", command=self.stop_monitoring, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def draw_meter_background(self):
        # Draw background markings
        # Green zone: -60dB to -12dB
        # Yellow zone: -12dB to -3dB
        # Red zone: -3dB to 0dB
        
        # Mapping dB to Y coordinates is linear for visual representation usually, 
        # but technically logarithmic. Here we will map -60 to 0 to 0% to 100% height
        
        pass 

    def populate_devices(self):
        self.devices = []
        self.device_map = {} # Name -> Index
        
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        
        default_index = -1
        try:
            default_index = self.p.get_default_input_device_info()['index']
        except:
            pass

        device_names = []
        
        for i in range(0, numdevices):
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                dev_info = self.p.get_device_info_by_host_api_device_index(0, i)
                base_name = dev_info.get('name')
                name = f"{base_name} ({i})"
                
                self.devices.append(i)
                self.device_map[name] = i
                device_names.append(name)
                
        self.combo_devices['values'] = device_names
        if device_names:
            # Try to select default
            if default_index in self.devices:
                for name, idx in self.device_map.items():
                    if idx == default_index:
                        self.combo_devices.set(name)
                        break
            else:
                self.combo_devices.current(0)

    def on_device_change(self, event):
        if self.is_running:
            self.stop_monitoring()
            self.start_monitoring()

    def start_monitoring(self):
        if not self.device_var.get():
            messagebox.showwarning("No Device", "Please select an audio device first.")
            return
            
        device_index = self.device_map[self.device_var.get()]
        
        try:
            self.stream = self.p.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      input_device_index=device_index,
                                      frames_per_buffer=self.CHUNK)
            self.is_running = True
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.combo_devices.config(state=tk.DISABLED)
            
            # Start processing thread
            self.thread = threading.Thread(target=self.audio_loop)
            self.thread.daemon = True
            self.thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open audio stream: {e}")

    def stop_monitoring(self):
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.combo_devices.config(state="readonly")
        
        # Reset meter
        self.update_meter(-100)

    def audio_loop(self):
        while self.is_running and self.stream:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                # Convert data to numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate RMS
                # Use float64 for better precision during square/mean
                rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
                
                # Calculate dB
                # Reference is 32768 (max value for 16-bit audio)
                if rms > 0:
                    db = 20 * np.log10(rms / 32768)
                else:
                    db = -100 # Silence
                
                # Schedule GUI update
                self.root.after(10, self.update_meter, db)
                
            except Exception as e:
                print(f"Error in audio loop: {e}")
                break

    def update_meter(self, db):
        # Clip dB to a reasonable range for display (e.g., -60 to 0)
        # Anything below -60 is effectively silence
        min_db = -60
        max_db = 0
        
        display_db = max(min_db, min(max_db, db))
        
        # Calculate percentage height
        # Range is 60dB
        if db < min_db:
            percent = 0
        else:
            percent = (display_db - min_db) / (max_db - min_db)
            
        # Update text
        if db <= -60:
            self.lbl_db.config(text="- inf dB")
        else:
            self.lbl_db.config(text=f"{db:.1f} dB")
            
        # Draw the active bar
        # canvas coords: (0, 0) is top-left
        bar_height = int(self.canvas_height * percent)
        y0 = self.canvas_height - bar_height
        y1 = self.canvas_height
        
        # Determine color based on level
        # Green < -12dB
        # Yellow -12dB to -3dB
        # Red > -3dB
        
        meter_color = "#00ff00" # Green
        if display_db > -3:
            meter_color = "#ff0000" # Red
        elif display_db > -12:
            meter_color = "#ffff00" # Yellow
            
        self.meter_canvas.coords(self.meter_bar, 0, y0, self.canvas_width, y1)
        self.meter_canvas.itemconfig(self.meter_bar, fill=meter_color)

    def on_closing(self):
        self.stop_monitoring()
        self.p.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioMeterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
