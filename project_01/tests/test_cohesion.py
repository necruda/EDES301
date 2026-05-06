"""
--------------------------------------------------------------------------
Cohesion Test - Corrected Hardware Pins
--------------------------------------------------------------------------
"""
import time
import subprocess
import sys
from screen_manager import ScreenManager
from button_manager import ButtonManager
from pot_manager import PotManager

def initialize_hardware():
    print("--- 1. Resetting Pin Muxing ---")
    # Using 'config-pin' to ensure the SPI pins are in the correct mode
    subprocess.run(["config-pin", "P1_08", "spi"], stderr=subprocess.DEVNULL)
    subprocess.run(["config-pin", "P1_10", "spi"], stderr=subprocess.DEVNULL)
    subprocess.run(["config-pin", "P1_12", "spi"], stderr=subprocess.DEVNULL)
    
    # GPIO pins for DC, CS, Reset and the 3 Buttons
    for pin in ["P1_04", "P1_06", "P1_02", "P2_28", "P2_30", "P2_32"]:
        subprocess.run(["config-pin", pin, "gpio"], stderr=subprocess.DEVNULL)

def run_integrated_test():
    initialize_hardware()
    
    # Initialize Managers with error catching
    try:
        screen = ScreenManager()
        pots = PotManager(timeline_steps=32)
        # Pins: Blue=28, Red=30, Black=32
        nav = ButtonManager(left_pin="P2_28", right_pin="P2_30", select_pin="P2_32")
        nav.start()
    except Exception as e:
        print(f"CRITICAL ERROR during Init: {e}")
        return

    # Logic Variables
    state = 0  # 0:Splash, 1:Browser, 2:Sequencer, 3:Modal, 4:Tempo
    carousel = ["RECORD", "PLAY", "PAUSE", "TEMPO", "CLEAR", "SAVE", "EXIT"]
    projects = ["HOUSE_KIT", "LOFI_BEATS", "TRAP_808"]
    
    current_bpm = 120
    is_editing_bpm = False 
    modal_type = ""

    print("--- 2. DRUMMY OS LIVE ---")
    print("System active. Press Black Button (P2_32) to transition.")

    try:
        while True:
            # 1. READ INPUTS
            pots.update()
            vol = pots.get_volume_midi()
            brt = pots.get_brightness_percent()
            step = pots.get_timeline_step()

            # --- SELECT BUTTON DEBOUNCE ---
            select_clicked = False
            if nav.btn_select.is_pressed():
                select_clicked = True
                # CRITICAL: Manually wait for the user to let go of the button
                while nav.btn_select.is_pressed():
                    time.sleep(0.01)
                print(f"CLICK: State {state}")

            # 2. CLEAR BUFFER (Mandatory for OLED refresh)
            screen.clear()

            # 3. STATE MACHINE DRAWING
            if state == 0:
                screen.draw_splash_screen()
                if select_clicked:
                    state = 1
                    nav.menu_index = 0

            elif state == 1:
                nav.max_index = len(projects)
                # Ensure HUD draws within browser for vol/brt visibility
                screen.draw_browser(projects, nav.menu_index, vol, brt)
                if select_clicked:
                    state = 2
                    nav.menu_index = 0

            elif state == 2:
                nav.max_index = len(carousel) - 1
                screen.draw_hud(vol, brt)
                # Draw 3 tracks as requested in logic
                screen.draw_sequencer_grid([[0,8,16], [4,12,20], [2,10,18]], step)
                screen.draw_footer_carousel(carousel, nav.menu_index)
                
                if select_clicked:
                    action = carousel[nav.menu_index]
                    if action == "TEMPO":
                        state = 4
                        nav.menu_index = 1
                    elif action in ["EXIT", "CLEAR", "SAVE"]:
                        modal_type = action
                        state = 3
                        nav.menu_index = 0

            elif state == 3:
                screen.draw_modal(f"{modal_type}?", "Confirm?", ["NO", "YES"], nav.menu_index)
                nav.max_index = 1
                if select_clicked:
                    if nav.menu_index == 1 and modal_type == "EXIT": 
                        break
                    state = 2
                    nav.menu_index = 0

            elif state == 4:
                nav.max_index = 2
                if is_editing_bpm:
                    # Sync BPM to Potentiometer (0-140 range)
                    current_bpm = int((step / 31) * 140)
                
                screen.draw_tempo_modal(current_bpm, nav.menu_index)
                
                if select_clicked:
                    if nav.menu_index == 1:
                        is_editing_bpm = not is_editing_bpm
                    else:
                        state = 2
                        is_editing_bpm = False

            # 4. PHYSICAL UPDATE
            # This pushes the "Whiteboard" to the hardware wires
            screen.display_show()
            
            # Small delay to prevent SPI bus flooding
            time.sleep(0.04)

    except KeyboardInterrupt:
        print("\nStopping Test...")
    finally:
        # Cleanup: Clear screen before exiting
        screen.clear()
        screen.display_show()

if __name__ == "__main__":
    run_integrated_test()