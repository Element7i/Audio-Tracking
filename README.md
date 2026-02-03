# Audio Level Meter

A Python-based GUI application to meter audio levels from a USB device or System Audio.

## Features
- Real-time decibel (dB) metering.
- Visual bar meter (Green/Yellow/Red zones).
- Input device selection.

## Setup

### Windows
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    python audio_meter.py
    ```

### macOS
1.  **Install PortAudio** (Required for PyAudio):
    You need Homebrew installed.
    ```bash
    brew install portaudio
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python audio_meter.py
    ```

### Linux
1.  **Install PortAudio** (Required for PyAudio):
    ```bash
    # Ubuntu/Debian
    sudo apt-get install portaudio19-dev python3-pyaudio
    
    # Fedora
    sudo dnf install portaudio-devel
    
    # Arch
    sudo pacman -S portaudio
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python audio_meter.py
    ```

## Usage

1. Launch the application using `python audio_meter.py`
2. Select your desired input device from the dropdown menu
3. Click "Start" to begin metering audio levels
4. The visual meter will display:
   - **Green**: Safe audio levels (below 60%)
   - **Yellow**: Moderate levels (60-85%)
   - **Red**: High levels (above 85%)
5. Click "Stop" to stop metering

## Requirements

- Python 3.7 or higher
- PyAudio
- NumPy
- tkinter (usually included with Python)

## Troubleshooting

### Windows
- If you encounter issues installing PyAudio, try using precompiled wheels:
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```

### macOS
- Make sure Homebrew is installed before installing PortAudio
- If you get permission errors, you may need to grant microphone access in System Preferences > Security & Privacy > Privacy > Microphone

### Linux
- If you encounter permission issues, you may need to add your user to the `audio` group:
  ```bash
  sudo usermod -aG audio $USER
  ```
  Then log out and log back in.
