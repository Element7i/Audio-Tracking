#!/usr/bin/env python3
"""
Audio Level Meter
A Python-based GUI application to meter audio levels from a USB device or System Audio.
"""

import tkinter as tk
from tkinter import ttk
import pyaudio
import numpy as np
import threading
import queue


class AudioMeter:
    """Main audio level meter application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Level Meter")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.REFERENCE_LEVEL = 32768  # For 16-bit audio
        
        # Audio stream
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.audio_queue = queue.Queue()
        
        # UI setup
        self.setup_ui()
        
        # Get available devices
        self.populate_devices()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the user interface."""
        # Title label
        title_label = tk.Label(
            self.root, 
            text="Audio Level Meter", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Device selection frame
        device_frame = tk.Frame(self.root)
        device_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(device_frame, text="Input Device:").pack(side=tk.LEFT)
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(
            device_frame, 
            textvariable=self.device_var,
            state="readonly",
            width=30
        )
        self.device_combo.pack(side=tk.LEFT, padx=10)
        self.device_combo.bind("<<ComboboxSelected>>", self.on_device_change)
        
        # dB level label
        self.db_label = tk.Label(
            self.root, 
            text="Level: -∞ dB", 
            font=("Arial", 14)
        )
        self.db_label.pack(pady=10)
        
        # Meter canvas
        self.canvas = tk.Canvas(self.root, width=360, height=60, bg="black")
        self.canvas.pack(pady=10)
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame, 
            text="Start", 
            command=self.start_meter,
            width=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            button_frame, 
            text="Stop", 
            command=self.stop_meter,
            width=10,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
    def populate_devices(self):
        """Populate the device dropdown with available input devices."""
        self.device_list = []
        
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                device_name = f"{i}: {info['name']}"
                self.device_list.append((i, device_name))
        
        if self.device_list:
            device_names = [name for _, name in self.device_list]
            self.device_combo['values'] = device_names
            self.device_combo.current(0)
        else:
            self.device_combo['values'] = ["No input devices found"]
            self.device_combo.current(0)
            
    def on_device_change(self, event):
        """Handle device selection change."""
        if self.running:
            self.stop_meter()
            
    def calculate_db(self, audio_data):
        """Calculate decibel level from audio data."""
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate RMS (Root Mean Square)
        # Convert to float to avoid overflow when squaring
        rms = np.sqrt(np.mean(audio_array.astype(np.float64)**2))
        
        # Avoid log of zero
        if rms < 1:
            return -np.inf
        
        # Convert to dB
        db = 20 * np.log10(rms / self.REFERENCE_LEVEL)
        
        return db
        
    def draw_meter(self, db_level):
        """Draw the meter bar based on dB level."""
        self.canvas.delete("all")
        
        # Normalize dB to 0-100 scale (assuming -60 dB to 0 dB range)
        if db_level == -np.inf:
            normalized = 0
        else:
            normalized = max(0, min(100, (db_level + 60) / 60 * 100))
        
        # Calculate bar width
        bar_width = int(normalized * 3.6)  # 360 pixels max
        
        # Determine color based on level
        if normalized < 60:
            color = "green"
        elif normalized < 85:
            color = "yellow"
        else:
            color = "red"
        
        # Draw the bar
        if bar_width > 0:
            self.canvas.create_rectangle(
                0, 0, bar_width, 60,
                fill=color,
                outline=""
            )
        
        # Draw scale markers
        for i in range(0, 361, 36):
            self.canvas.create_line(
                i, 50, i, 60,
                fill="white",
                width=1
            )
            
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream."""
        self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
        
    def update_meter(self):
        """Update meter display from audio queue."""
        try:
            while not self.audio_queue.empty():
                audio_data = self.audio_queue.get_nowait()
                db_level = self.calculate_db(audio_data)
                
                # Update label
                if db_level == -np.inf:
                    self.db_label.config(text="Level: -∞ dB")
                else:
                    self.db_label.config(text=f"Level: {db_level:.1f} dB")
                
                # Update meter
                self.draw_meter(db_level)
        except queue.Empty:
            pass
        
        if self.running:
            self.root.after(50, self.update_meter)
            
    def start_meter(self):
        """Start the audio metering."""
        if not self.device_list:
            return
            
        # Get selected device
        selected_index = self.device_combo.current()
        if selected_index < 0:
            return
            
        device_index = self.device_list[selected_index][0]
        
        try:
            # Open audio stream
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.CHUNK,
                stream_callback=self.audio_callback
            )
            
            self.stream.start_stream()
            self.running = True
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.device_combo.config(state=tk.DISABLED)
            
            # Start updating meter
            self.update_meter()
            
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.running = False
            
    def stop_meter(self):
        """Stop the audio metering."""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.device_combo.config(state="readonly")
        
        # Reset display
        self.db_label.config(text="Level: -∞ dB")
        self.canvas.delete("all")
        
    def on_closing(self):
        """Handle window close event."""
        self.stop_meter()
        self.p.terminate()
        self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = AudioMeter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
