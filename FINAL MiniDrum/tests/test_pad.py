"""
--------------------------------------------------------------------------
Performance Pad Test Utility
--------------------------------------------------------------------------
"""
import subprocess
import time
from pad_manager import PadManager

def setup_hardware(pins):
    """Ensure the kernel has set the pins to GPIO mode."""
    print("Configuring Pinmux...")
    for pin in pins:
        try:
            subprocess.run(["config-pin", pin, "gpio"], check=True)
            print(f"  [OK] {pin} set to GPIO")
        except Exception as e:
            print(f"  [ERROR] Could not configure {pin}: {e}")

def run_test():
    # 1. Define the pins as per your Rev A2a diagram selection
    pad_pins = ["P2_19", "P2_22", "P2_24"]
    
    # 2. Run system config
    setup_hardware(pad_pins)
    
    # 3. Initialize the Manager
    # Mapping: Kick=P2_04, Snare=P2_06, Hat=P2_08
    pads = PadManager(kick_pin="P2_19", snare_pin="P2_22", hat_pin="P2_24")
    
    print("\n--- PERFORMANCE PAD TEST ---")
    print("Drum away! Press Ctrl+C to finish the session.")
    
    try:
        pads.start()
        
        # Keep the main thread alive with a visual 'pulse'
        while True:
            # The pads run on their own threads, so this loop 
            # just keeps the script from exiting.
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping Pad Manager...")
        pads.stop()
        print("Test Session Ended.")

if __name__ == "__main__":
    run_test()