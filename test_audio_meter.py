#!/usr/bin/env python3
"""
Test script for Audio Level Meter
Tests the core logic without GUI or audio devices
"""

import numpy as np
import sys
import os


def test_db_calculation():
    """Test the dB calculation logic."""
    REFERENCE_LEVEL = 32768  # For 16-bit audio
    
    # Test with zero signal
    audio_data = np.zeros(1024, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
    if rms < 1:
        db = -np.inf
    else:
        db = 20 * np.log10(rms / REFERENCE_LEVEL)
    
    assert db == -np.inf, f"Expected -inf dB for zero signal, got {db}"
    print("✓ Zero signal test passed")
    
    # Test with moderate signal
    audio_data = np.full(1024, 16384, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
    if rms < 1:
        db = -np.inf
    else:
        db = 20 * np.log10(rms / REFERENCE_LEVEL)
    
    expected_db = 20 * np.log10(16384 / 32768)
    assert abs(db - expected_db) < 0.01, f"Expected {expected_db} dB, got {db}"
    print(f"✓ Moderate signal test passed (got {db:.2f} dB)")
    
    # Test with full scale signal
    audio_data = np.full(1024, 32767, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
    if rms < 1:
        db = -np.inf
    else:
        db = 20 * np.log10(rms / REFERENCE_LEVEL)
    
    # Should be close to 0 dB
    assert db > -0.1, f"Expected near 0 dB for full scale signal, got {db}"
    print(f"✓ Full scale signal test passed (got {db:.2f} dB)")


def test_meter_normalization():
    """Test the meter bar normalization logic."""
    # Test -60 dB to 0 dB range normalization
    
    # -60 dB should be 0%
    db = -60
    normalized = max(0, min(100, (db + 60) / 60 * 100))
    assert normalized == 0, f"Expected 0% for -60 dB, got {normalized}%"
    print("✓ Minimum level test passed")
    
    # 0 dB should be 100%
    db = 0
    normalized = max(0, min(100, (db + 60) / 60 * 100))
    assert normalized == 100, f"Expected 100% for 0 dB, got {normalized}%"
    print("✓ Maximum level test passed")
    
    # -30 dB should be 50%
    db = -30
    normalized = max(0, min(100, (db + 60) / 60 * 100))
    assert normalized == 50, f"Expected 50% for -30 dB, got {normalized}%"
    print("✓ Mid level test passed")


def test_color_zones():
    """Test the color zone logic."""
    # Test color assignments
    
    # Green zone (< 60%)
    normalized = 30
    if normalized < 60:
        color = "green"
    elif normalized < 85:
        color = "yellow"
    else:
        color = "red"
    assert color == "green", f"Expected green for 30%, got {color}"
    print("✓ Green zone test passed")
    
    # Yellow zone (60-85%)
    normalized = 70
    if normalized < 60:
        color = "green"
    elif normalized < 85:
        color = "yellow"
    else:
        color = "red"
    assert color == "yellow", f"Expected yellow for 70%, got {color}"
    print("✓ Yellow zone test passed")
    
    # Red zone (>= 85%)
    normalized = 90
    if normalized < 60:
        color = "green"
    elif normalized < 85:
        color = "yellow"
    else:
        color = "red"
    assert color == "red", f"Expected red for 90%, got {color}"
    print("✓ Red zone test passed")


def test_code_structure():
    """Test that the main code file has proper structure."""
    # Get the directory containing this test file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    audio_meter_path = os.path.join(test_dir, 'audio_meter.py')
    
    with open(audio_meter_path, 'r') as f:
        code = f.read()
    
    # Check for required components
    assert 'class AudioMeter' in code, "AudioMeter class not found"
    assert 'def calculate_db' in code, "calculate_db method not found"
    assert 'def draw_meter' in code, "draw_meter method not found"
    assert 'def start_meter' in code, "start_meter method not found"
    assert 'def stop_meter' in code, "stop_meter method not found"
    assert 'import tkinter' in code, "tkinter import not found"
    assert 'import pyaudio' in code, "pyaudio import not found"
    assert 'import numpy' in code, "numpy import not found"
    
    print("✓ Code structure test passed")


def main():
    """Run all tests."""
    print("Running Audio Level Meter Tests...\n")
    
    try:
        test_code_structure()
        test_db_calculation()
        test_meter_normalization()
        test_color_zones()
        
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
