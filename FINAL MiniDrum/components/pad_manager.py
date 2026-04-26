"""
--------------------------------------------------------------------------
Performance Pad Manager
--------------------------------------------------------------------------
This module handles the high-speed drum triggers for the project.
--------------------------------------------------------------------------
"""
from threaded_input import ThreadedInput
import time

class PadManager:
    def __init__(self, kick_pin="P2_19", snare_pin="P2_22", hat_pin="P2_24"):
        # Initialize ThreadedInputs with your specific P2 pins
        # Debounce remains 20ms for high-speed response
        self.pads = {
            "KICK":   ThreadedInput(kick_pin, label="KICK", debounce_ms=20),
            "SNARE":  ThreadedInput(snare_pin, label="SNARE", debounce_ms=20),
            "HI-HAT": ThreadedInput(hat_pin, label="HI-HAT", debounce_ms=20)
        }

        # New Feature: A 'Queue' to store hits until the main loop is ready to read them
        self.hit_queue = []
        
        # New Feature: Track 'Velocity' (defaulting to 100 for touch pads)
        self.default_velocity = 100

    def start(self):
        """Initialize all threads and bind them to the internal handlers."""
        print("Initializing Performance Pads (Rev A2a - Threaded)...")
        
        # We bind each ThreadedInput to a generic handler that feeds our queue
        self.pads["KICK"].start(on_press=lambda: self._register_hit("KICK"))
        self.pads["SNARE"].start(on_press=lambda: self._register_hit("SNARE"))
        self.pads["HI-HAT"].start(on_press=lambda: self._register_hit("HI-HAT"))

    def _register_hit(self, pad_name):
        """Internal callback: adds a hit to the queue for the main loop to find."""
        timestamp = time.time()
        # We store the name and the current 'velocity'
        self.hit_queue.append((pad_name, self.default_velocity, timestamp))
        
        # Keep the old print statements for your diagnostics
        symbol = "BOOM!" if pad_name == "KICK" else "CRACK!" if pad_name == "SNARE" else "TISS!"
        print(f"[{timestamp:.3f}] {symbol} {pad_name} Triggered")

    def get_new_hits(self):
        """
        New Feature: Main script calls this to get all hits since the last check.
        Returns a list of (name, velocity) tuples.
        """
        current_hits = self.hit_queue[:]
        self.hit_queue = [] # Clear the queue after reading
        return current_hits

    def is_pad_pressed(self, pad_name):
        """New Feature: Check if a finger is CURRENTLY on the pad (useful for UI)."""
        if pad_name in self.pads:
            return self.pads[pad_name].is_pressed()
        return False

    def stop(self):
        """Shut down all monitoring threads safely."""
        for pad in self.pads.values():
            pad.stop()