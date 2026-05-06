"""
--------------------------------------------------------------------------
Potentiometer Manager
--------------------------------------------------------------------------
"""
import Adafruit_BBIO.ADC as ADC
import time

class PotManager:
    def __init__(self, timeline_steps=21):
        ADC.setup()
        self.pot_config = {
            "TIMELINE": "AIN0", 
            "VOLUME":   "AIN1", 
            "BRIGHT":   "AIN2"  
        }
        self.values = {name: 0.8 for name in self.pot_config}
        self.timeline_steps = timeline_steps
        self.smoothing = 0.15 
        self.last_read_time = 0

    def update(self):
        # NEW: Only read every 30ms. This gives the Screen SPI bus room to breathe.
        current_time = time.time()
        if current_time - self.last_read_time < 0.03:
            return

        for name, pin in self.pot_config.items():
            try:
                raw_reading = ADC.read(pin)
                if raw_reading is not None:
                    # Smoothing prevents the screen from flickering when the pot is still
                    self.values[name] = (raw_reading * self.smoothing) + \
                                        (self.values[name] * (1.0 - self.smoothing))
            except:
                continue
        self.last_read_time = current_time

    def get_timeline_step(self):
        # This ensures equal distribution across the rotation
        step = int(self.values["TIMELINE"] * self.timeline_steps)
        return max(0, min(step, self.timeline_steps - 1))

    def get_volume_midi(self):
        return int(self.values["VOLUME"] * 100)

    def get_brightness_percent(self):
        return int(self.values["BRIGHT"] * 100)