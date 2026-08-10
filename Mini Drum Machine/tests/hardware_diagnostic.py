"""
--------------------------------------------------------------------------
PocketBeagle Unified Hardware Diagnostic Tool
--------------------------------------------------------------------------
"""
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import time

class SystemDiagnostic:
    def __init__(self):
        self.pots    = {"Brightness": "P1_19", "Volume": "P1_21", "Master": "P1_23"}
        self.buttons = {"Blue (Left)": "P2_28", "Red (Right)": "P2_30", "Black (Select)": "P2_32"}
        # UPDATED PINS HERE:
        self.pads    = {"Kick": "P2_19", "Snare": "P2_22", "Hat": "P2_24"}
        self._initialize_hardware()
        self._initialize_hardware()

    def _initialize_hardware(self):
        print("Starting ADC...")
        ADC.setup()
        
        print("Setting up GPIO pins...")
        for name, pin in {**self.buttons, **self.pads}.items():
            try:
                # We try setup WITHOUT pull-up first to see if that's the crash point
                GPIO.setup(pin, GPIO.IN)
                print(f"  [OK] {name} ({pin})")
            except Exception as e:
                print(f"  [FAIL] {name} ({pin}): {e}")

    def run(self):
        print("\n--- MONITORING HARDWARE (CTRL+C to STOP) ---")
        try:
            while True:
                # Analog Read
                ana_str = ""
                for name, pin in self.pots.items():
                    val = ADC.read(pin) * 1.8
                    ana_str += f"{name}: {val:.2f}V | "
                
                # Digital Read
                dig_str = ""
                for name, pin in {**self.buttons, **self.pads}.items():
                    state = "HIGH" if GPIO.input(pin) else "LOW"
                    dig_str += f"{name}: {state} | "
                
                print(f"ANA: {ana_str}")
                print(f"DIG: {dig_str}")
                print("-" * 30)
                time.sleep(0.5)
        except KeyboardInterrupt:
            GPIO.cleanup()

if __name__ == "__main__":
    tester = SystemDiagnostic()
    tester.run()