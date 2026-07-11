"""Quick 5-second audio test"""
import pygame
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
athan_path = PROJECT_ROOT / "src/assets/athan.wav"

print("Initializing audio...")
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.music.set_volume(1.0)

print(f"\n🔊 Playing athan for 5 seconds...")
print("LISTEN NOW - you should hear the call to prayer!")

pygame.mixer.music.load(str(athan_path))
pygame.mixer.music.play()

print("\n⏳ Playing... ", end="", flush=True)
for i in range(5):
    time.sleep(1)
    print(f"{i+1}s...", end=" ", flush=True)

pygame.mixer.music.stop()
print("\n\n✅ Test complete!")
print("\nDid you hear the athan (call to prayer)?")
print("  YES → Prayer alerts are working correctly!")
print("  NO  → Check your system volume and speakers/headphones")
