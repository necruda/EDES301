import Adafruit_BBIO.GPIO as GPIO
import threading
import time

# --- The Class ---
class ThreadedInput:
    def __init__(self, pin, label="Input", debounce_ms=50):
        self.pin = pin
        self.label = label
        self.debounce_s = debounce_ms / 1000.0
        self.callback = None
        self._running = False
        self._thread = None
        self._setup()

    def _setup(self):
        # Rule 5: Configured for 3.3V logic with internal pull-up
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _monitor(self):
        last_state = GPIO.HIGH
        while self._running:
            current_state = GPIO.input(self.pin)
            # Detect transition from HIGH (idle) to LOW (pressed)
            if current_state == GPIO.LOW and last_state == GPIO.HIGH:
                if self.callback:
                    self.callback()
                time.sleep(self.debounce_s)
            last_state = current_state
            time.sleep(0.005) 

    def start(self, callback_function):
        self.callback = callback_function
        self._running = True
        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._thread.start()
        print(f"  [READY] {self.label} listening on {self.pin}")

    def stop(self):
        self._running = False

# --- The Test ---
if __name__ == "__main__":
    # Define the response
    def my_button_action():
        print("\n[ACTION] P2_32 (Black Button) pressed! Threading is working.")

    # Create the object
    select_btn = ThreadedInput(pin="P2_32", label="Select Button")

    print("Configuring P2_32...")
    # Terminal-style setup check
    import subprocess
    subprocess.run(["config-pin", "P2_32", "gpio"])

    select_btn.start(callback_function=my_button_action)

    try:
        print("Waiting for presses. (Press Ctrl+C to stop)")
        while True:
            # We print a small pulse to show the main thread isn't blocked
            print(".", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTest complete.")
        select_btn.stop()
        GPIO.cleanup()