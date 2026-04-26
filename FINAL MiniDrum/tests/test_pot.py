from pot_manager import PotManager
import time
import os

def draw_bar(label, value, max_val, bar_length=20):
    """Creates a visual [#####     ] progress bar for the terminal."""
    percent = value / max_val
    filled = int(bar_length * percent)
    bar = "█" * filled + "-" * (bar_length - filled)
    return f"{label:10} |{bar}| {value:3}"

def main():
    # Initialize with 16 steps for the Timeline Scroll
    pm = PotManager(timeline_steps=21)
    
    print("--- MiniDrum Potentiometer Live Test ---")
    print("Hardware: P1_19 (AIN0), P1_21 (AIN1), P1_23 (AIN2)")
    print("Wiring: Ensure Pots are powered by 1.8V (P1_18)")
    print("Press Ctrl+C to exit.\n")
    
    try:
        while True:
            # 1. Update the readings
            pm.update()
            
            # 2. Get the processed values
            step = pm.get_timeline_step()
            vol  = pm.get_volume_midi()
            brt  = pm.get_brightness_percent()
            
            # 3. Build visual bars
            # Scale: Step (0-15), Vol (0-127), Bright (0-100)
            step_bar = draw_bar("TIMELINE", step, 20)
            vol_bar  = draw_bar("VOLUME",   vol,  100)
            brt_bar  = draw_bar("BRIGHT",   brt,  100)
            
            # 4. Print and refresh
            # Using \033[F to move the cursor up 3 lines to overwrite
            print(f"{step_bar}\n{vol_bar}\n{brt_bar}")
            print("\033[F" * 3, end="")
            
            time.sleep(0.05) # 20 updates per second
            
    except KeyboardInterrupt:
        print("\n\nTest Finished. If bars were jumpy, try decreasing 'smoothing' in pot_manager.py.")

if __name__ == "__main__":
    main()