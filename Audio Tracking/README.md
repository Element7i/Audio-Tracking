<<<<<<< HEAD
# Audio-Tracking
audio meter I Made, I just feel like its better when I make my own.
=======
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
    *Note: If installation fails, try:*
    ```bash
    pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
    ```

## Usage

1.  Run the script:
    ```bash
    python audio_meter.py
    ```
2.  Select your input device from the dropdown.

### How to measure System Audio (What you hear)

**On Windows:**
To measure the audio playing on your computer (Youtube, Spotify, etc.), you usually need to enable "Stereo Mix".
1.  Open Sound Settings -> Sound Control Panel?
2.  Go to the **Recording** tab.
3.  Right-click and ensure "Show Disabled Devices" is checked.
4.  Find **Stereo Mix**, right-click, and **Enable** it.
5.  Restart this application and select "Stereo Mix" from the dropdown.

**On Mac:**
You may need a virtual audio driver like **BlackHole** or **Soundflower** to route system output to an input device that this app can read.

## Troubleshooting

-   If you get an error about "No Default Input Device", ensure you have a microphone or audio interface connected.
-   If the meter is stuck at -inf, ensure the correct device is selected and audio is actually playing/going into that device.
>>>>>>> 7293358 (Initial commit - Audio Meter App)
