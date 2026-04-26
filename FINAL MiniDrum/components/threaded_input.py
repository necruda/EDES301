"""
--------------------------------------------------------------------------
Threaded Digital Input Driver
--------------------------------------------------------------------------
"""
import Adafruit_BBIO.GPIO as GPIO
import threading
import time

class ThreadedInput:
    def __init__(self, pin, label="Input", debounce_ms=50):
        self.pin = pin
        self.label = label
        self.debounce_s = debounce_ms / 1000.0
        
        self.on_press_func = None
        self.on_release_func = None
        
        # NEW: Click Latching
        self._was_clicked = False
        
        self._running = False
        self._thread = None
        
        self._setup()

    def _setup(self):
        # Configure for 3.3V GPIO with Pull-Up
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        """Returns the REAL-TIME hardware state."""
        return GPIO.input(self.pin) == GPIO.LOW

    def was_clicked(self):
        """
        NEW HELPER: Use this in drummy_os.py for the 'Select' button.
        Returns True if a click happened since the last time this was called.
        """
        if self._was_clicked:
            self._was_clicked = False # Reset the latch
            return True
        return False

    def _monitor(self):
        """Background thread to detect hits with low latency."""
        time.sleep(0.1) 
        last_state = GPIO.input(self.pin)
        
        while self._running:
            current_state = GPIO.input(self.pin)
            
            # Detect Falling Edge (Press)
            if current_state == GPIO.LOW and last_state == GPIO.HIGH:
                self._was_clicked = True # Latch the click for the main loop
                
                if self.on_press_func:
                    try:
                        self.on_press_func()
                    except Exception as e:
                        print(f"Error in {self.label} callback: {e}")
                
                time.sleep(self.debounce_s)
            
            # Detect Rising Edge (Release)
            elif current_state == GPIO.HIGH and last_state == GPIO.LOW:
                if self.on_release_func:
                    try:
                        self.on_release_func()
                    except Exception as e:
                        print(f"Error in {self.label} release callback: {e}")
                
            last_state = current_state
            time.sleep(0.01) # Slightly slower poll (100Hz) to save CPU for the Screen

    def start(self, on_press=None, on_release=None):
        self.on_press_func = on_press
        self.on_release_func = on_release
        self._running = True
        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._thread.start()
        print(f"  [READY] {self.label} active on {self.pin}")

    def stop(self):
        self._running = False