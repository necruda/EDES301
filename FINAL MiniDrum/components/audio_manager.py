"""
--------------------------------------------------------------------------
Audio Manager
--------------------------------------------------------------------------
"""
import subprocess
import os

class AudioManager:
    # Use the absolute path to your MiniDrum project folder
    def __init__(self, sample_folder="/var/lib/cloud9/EDES301/MiniDrum/samples"):
        self.sample_folder = sample_folder
        # ... rest of your code ...
        
        self.samples = {
            0: "kick.wav",
            1: "snare.wav",
            2: "hihat.wav",
            3: "metronome_high.wav", 
            4: "metronome_low.wav"  
        }
        
        if not os.path.exists(self.sample_folder):
            print(f"CRITICAL: Sample folder {self.sample_folder} not found.")

    def play_sample(self, pad_index, volume=100):
        """Play sample with a specific volume (0-100)"""
        if pad_index in self.samples:
            filename = self.samples[pad_index]
            filepath = os.path.join(self.sample_folder, filename)
            
            if os.path.exists(filepath):
                # Ensure volume is an integer between 0 and 100
                vol_str = str(int(max(0, min(volume, 100))))
                
                subprocess.Popen(
                    ["mplayer", "-really-quiet", "-noconsolecontrols", 
                     "-ao", "alsa:device=hw=1,0",
                     "-volume", vol_str, filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                print(f"Missing File: {filepath}")