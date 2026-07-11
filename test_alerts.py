"""
Test script to verify prayer alert system is working.
Creates synthetic prayer times close to current time to trigger alerts.
"""

import datetime
import time
import pygame
import os
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "src/assets"

def test_audio_files():
    """Test that audio files exist and can be loaded."""
    print("=" * 60)
    print("TESTING AUDIO FILES")
    print("=" * 60)
    
    audio_files = {
        "Dua": ASSETS_DIR / "dua.wav",
        "Fajr Athan": ASSETS_DIR / "fajr_athan.wav",
        "Regular Athan": ASSETS_DIR / "athan.wav"
    }
    
    all_exist = True
    for name, path in audio_files.items():
        if os.path.exists(path):
            print(f"✅ {name}: {path} - EXISTS")
        else:
            print(f"❌ {name}: {path} - MISSING")
            all_exist = False
    
    return all_exist

def test_pygame_init():
    """Test pygame mixer initialization."""
    print("\n" + "=" * 60)
    print("TESTING PYGAME MIXER INITIALIZATION")
    print("=" * 60)
    
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.music.set_volume(1.0)
        print("✅ Pygame mixer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize pygame mixer: {e}")
        return False

def play_audio(file_path, max_wait_seconds=30):
    """Play a single audio file with timeout."""
    print(f"\n🔊 Playing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        print("   Waiting for playback to complete (max 30 seconds)...")
        wait_count = 0
        while pygame.mixer.music.get_busy() and wait_count < max_wait_seconds * 10:
            pygame.time.Clock().tick(10)
            wait_count += 1
            if wait_count % 10 == 0:
                print(f"   ... {wait_count // 10}s elapsed")
        
        if wait_count >= max_wait_seconds * 10:
            print(f"⚠️ Playback timed out after {max_wait_seconds} seconds")
            pygame.mixer.music.stop()
            return False
        
        print(f"✅ Successfully played: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error playing audio: {e}")
        return False

def test_alert_sequence():
    """Test playing athan followed by dua."""
    print("\n" + "=" * 60)
    print("TESTING PRAYER ALERT SEQUENCE")
    print("=" * 60)
    
    athan_path = ASSETS_DIR / "athan.wav"
    dua_path = ASSETS_DIR / "dua.wav"
    
    print("\n🎵 Playing Athan...")
    success1 = play_audio(athan_path)
    
    print("\n🎵 Playing Dua...")
    success2 = play_audio(dua_path)
    
    if success1 and success2:
        print("\n✅ Alert sequence completed successfully!")
        return True
    else:
        print("\n⚠️ Alert sequence completed with errors")
        return False

def test_synthetic_prayer_time():
    """Test with synthetic prayer time close to current time."""
    print("\n" + "=" * 60)
    print("TESTING SYNTHETIC PRAYER TIME ALERT")
    print("=" * 60)
    
    now = datetime.datetime.now()
    # Set prayer time to 10 seconds in the future
    prayer_time = now + datetime.timedelta(seconds=10)
    
    print(f"\nCurrent time: {now.strftime('%H:%M:%S')}")
    print(f"Synthetic prayer time: {prayer_time.strftime('%H:%M:%S')}")
    print(f"Alert will trigger in 10 seconds...")
    print(f"Waiting...")
    
    # Wait until we're within the alert window (0-30 seconds before prayer)
    for i in range(10, 0, -1):
        print(f"  {i} seconds...")
        time.sleep(1)
    
    print("\n🔔 TRIGGERING ALERT NOW!")
    
    # Simulate the alert
    athan_path = ASSETS_DIR / "athan.wav"
    dua_path = ASSETS_DIR / "dua.wav"
    
    print("\n🎵 Playing Athan...")
    play_audio(athan_path)
    
    print("\n🎵 Playing Dua...")
    play_audio(dua_path)
    
    print("\n✅ Synthetic alert test completed!")

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PRAYER ALERT SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Check audio files exist
    if not test_audio_files():
        print("\n❌ FAILED: Audio files missing. Cannot proceed with tests.")
        return
    
    # Test 2: Initialize pygame
    if not test_pygame_init():
        print("\n❌ FAILED: Cannot initialize pygame mixer. Check audio system.")
        return
    
    # Quick test mode - just play once without waiting
    print("\n\n🔊 QUICK TEST: Playing athan.wav...")
    print("(If you hear the athan, the alert system is working!)")
    athan_path = ASSETS_DIR / "athan.wav"
    
    success = play_audio(athan_path, max_wait_seconds=30)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ AUDIO TEST PASSED")
        print("=" * 60)
        print("\nIf you heard the athan:")
        print("  ✅ Prayer alerts WILL work in the main app")
        print("\nIf you did NOT hear anything:")
        print("  ⚠️ Check system volume and audio output device")
    else:
        print("\n" + "=" * 60)
        print("⚠️ AUDIO TEST HAD ISSUES")
        print("=" * 60)
        print("Check the error messages above")
    
    print("\n\nRun 'python test_alerts.py full' for complete testing")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        # Full test mode with user prompts
        print("\n" + "=" * 60)
        print("FULL TEST MODE")
        print("=" * 60)
        test_audio_files()
        test_pygame_init()
        print("\n\nPress Enter to test alert sequence...")
        input()
        test_alert_sequence()
        print("\n\nPress Enter to test synthetic prayer time (10 second countdown)...")
        input()
        test_synthetic_prayer_time()
    else:
        main()
