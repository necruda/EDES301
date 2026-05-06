"""
--------------------------------------------------------------------------
DrummyOS - Final Integrated Version
--------------------------------------------------------------------------
"""
import time
import sys
import os
import board
import digitalio
from screen_manager import ScreenManager
from button_manager import ButtonManager
from pot_manager import PotManager
from pad_manager import PadManager
from audio_manager import AudioManager
from project_manager import ProjectManager

# --- State Constants (Aligned with Old Version) ---
STATE_SPLASH    = 0
STATE_BROWSER   = 1
STATE_SEQUENCER = 2
STATE_MODAL     = 3
STATE_TEMPO     = 4

class DrummyOS:
    def __init__(self):
        # 1. Initialize Hardware Managers
        self.screen = ScreenManager()
        self.pots   = PotManager(timeline_steps=32)
        # Using the New ButtonManager but ensuring pins match your hardware
        self.nav    = ButtonManager(left_pin="P2_28", right_pin="P2_30", select_pin="P2_32")
        
        self.audio = AudioManager()
        self.pads  = PadManager()
        self.pads.start()
        self.pm    = ProjectManager()

        # 2. System State
        self.state = STATE_SPLASH 
        self.carousel = ["RECORD", "PLAY", "STOP", "TEMPO", "CLEAR", "SAVE", "EXIT"]
        
        self.projects = self.pm.get_project_list()
        self.current_project_name = "UNTITLED"
        self.selected_project_temp = "" 
        
        # Initialize grid with 0s (3 rows x 32 steps)
        self.grid_data = [[], [], []]
        
        # 3. Playback Engine State
        self.is_playing = False
        self.is_recording = False 
        self.playhead = 0           
        self.last_tick_time = 0    
        
        self.modal_type = ""
        self.current_bpm = 120
        
        # Start Input Threads
        self.nav.start()

    def run(self):
        print("Drummy 3000 OS Booted.")
        while True:
            # Global Input Updates
            self.pots.update()
            vol = self.pots.values.get("VOLUME", 0.8) * 100
            brt = self.pots.values.get("BRIGHT", 0.8) * 100
            cursor = self.pots.get_timeline_step()
            
            select_clicked = self.nav.btn_select.was_clicked()
            
            # STATE MACHINE
            if self.state == STATE_SPLASH:
                self.screen.draw_splash_screen()
                if int(time.time() * 2) % 2 == 0:
                    self.screen.draw_text_aligned("PRESS SELECT", 50)
                if select_clicked:
                    self.state = STATE_BROWSER
                    time.sleep(0.3)
            
            elif self.state == STATE_BROWSER:
                self.handle_browser_logic(vol, brt, select_clicked)

            elif self.state == STATE_SEQUENCER:
                self.update_sequencer_engine() # Only process audio engine in sequencer mode
                self.handle_sequencer_ui(vol, brt, cursor, select_clicked)

            elif self.state == STATE_MODAL:
                self.handle_modal_logic(select_clicked)

            elif self.state == STATE_TEMPO:
                self.handle_tempo_logic(cursor, select_clicked)

            # Final Render
            self.screen.display_show()
            time.sleep(0.05) # Breath for the CPU/SPI bus

    def update_sequencer_engine(self):
        """Calculates timing and triggers audio hits."""
        hits = self.pads.get_new_hits()
        for pad_name, vel, ts in hits:
            idx = {"KICK":0, "SNARE":1, "HI-HAT":2}.get(pad_name, 0)
            self.audio.play_sample(idx)
            if self.is_recording and self.is_playing:
                if self.playhead not in self.grid_data[idx]:
                    self.grid_data[idx].append(self.playhead)
    
        if not self.is_playing:
            # When stopped, sync playhead to the dial position
            self.playhead = self.pots.get_timeline_step()
            return
    
        # Playback Timing
        tick_duration = (60.0 / self.current_bpm) / 8.0
        now = time.time()
    
        if now - self.last_tick_time >= tick_duration:
            self.playhead = (self.playhead + 1) % 32
            self.last_tick_time = now
    
            if self.playhead % 8 == 0:
                self.audio.play_sample(3 if self.playhead == 0 else 4)
    
            for track_idx in range(3):
                if self.playhead in self.grid_data[track_idx]:
                    self.audio.play_sample(track_idx)

    def handle_sequencer_ui(self, vol, brt, cursor, select_clicked):
        self.nav.max_index = len(self.carousel) - 1
        self.screen.clear()
        self.screen.draw_hud(vol, brt)
        self.screen.draw_sequencer_grid(self.grid_data, cursor, self.playhead)
        self.screen.draw_footer_carousel(self.carousel, self.nav.menu_index)

        if select_clicked:
            action = self.carousel[self.nav.menu_index]
            self.handle_action(action)
            time.sleep(0.2)

    def handle_action(self, action):
        if action == "PLAY":
            if not self.is_recording:
                self.is_playing = True
                self.playhead = self.pots.get_timeline_step()  # start from dial position
                self.last_tick_time = time.time()
        
        elif action == "STOP":
            if not self.is_recording:  # STOP does nothing if recording is active
                self.is_playing = False
                # Playhead intentionally NOT reset — stays at current position
        
        elif action == "RECORD":
            if not self.is_recording:
                self.is_recording = True
                if not self.is_playing:
                    self.is_playing = True
                    self.playhead = self.pots.get_timeline_step()  # start from dial position
                    self.last_tick_time = time.time()
            else:
                self.is_recording = False
                self.is_playing = False
        
        elif action == "TEMPO":
            self.state = STATE_TEMPO
            self.nav.menu_index = 1
        
        elif action == "CLEAR":
            self.modal_type = "CLEAR"
            self.state = STATE_MODAL
        
        elif action == "SAVE":
            name = f"PROJECT_{int(time.time())}"
            self.pm.save(name, self.grid_data, self.current_bpm)
            self.current_project_name = name
        
        elif action == "EXIT":
            self.modal_type = "EXIT"
            self.state = STATE_MODAL

    def handle_browser_logic(self, vol, brt, select_clicked):
        self.screen.clear()
        # Add a "New Project" option so the list isn't empty
        options = ["+ NEW PROJECT"] + self.projects
        self.nav.max_index = max(0, len(options) - 1)
        
        # Use the options list you just made, not self.projects
        self.screen.draw_browser(self.projects, self.nav.menu_index, vol, brt)
        
        if select_clicked:
            if self.nav.menu_index == 0: 
                self.grid_data = [[], [], []]
                self.state = STATE_SEQUENCER
            else:
                self.selected_project_temp = self.projects[self.nav.menu_index - 1]
                self.modal_type = "LOAD"
                self.state = STATE_MODAL
            
            self.nav.menu_index = 0
            time.sleep(0.3)

    def handle_modal_logic(self, select_clicked):
        if self.modal_type == "LOAD":
            self.nav.max_index = 2  # Now 3 options: 0, 1, 2
            options = ["BACK", "DEL", "LOAD"]
            self.screen.draw_modal("PROJECT OPTION", self.selected_project_temp, options, self.nav.menu_index)
            if select_clicked:
                if self.nav.menu_index == 0:  # BACK
                    self.state = STATE_BROWSER
                elif self.nav.menu_index == 1:  # DELETE
                    self.pm.delete(self.selected_project_temp)
                    self.projects = self.pm.get_project_list()  # refresh list
                    self.state = STATE_BROWSER
                elif self.nav.menu_index == 2:  # LOAD
                    grid, bpm = self.pm.load(self.selected_project_temp)
                    if grid is not None:
                        self.grid_data = grid
                        self.current_bpm = bpm
                        self.current_project_name = self.selected_project_temp
                        self.playhead = 0
                        self.state = STATE_SEQUENCER
                self.nav.menu_index = 0
                time.sleep(0.3)
        else:
            self.nav.max_index = 1
            options = ["CANCEL", "OK"]
            self.screen.draw_modal(f"{self.modal_type}?", "Are you sure?", options, self.nav.menu_index)
            if select_clicked:
                if self.nav.menu_index == 1:
                    if self.modal_type == "EXIT":
                        self.pads.stop()
                        sys.exit()
                    elif self.modal_type == "CLEAR":
                        self.grid_data = [[], [], []]
                self.state = STATE_SEQUENCER
                self.nav.menu_index = 0
                time.sleep(0.3)

    def handle_tempo_logic(self, cursor, select_clicked):
        self.nav.max_index = 2 
        if self.nav.menu_index == 1: # Value Slider active
            self.current_bpm = int((cursor / 31.0) * 140) + 40
            
        self.screen.draw_tempo_modal(self.current_bpm, self.nav.menu_index)
        
        if select_clicked:
            if self.nav.menu_index in [0, 2]: # OK or CANCEL
                self.state = STATE_SEQUENCER
            time.sleep(0.3)

if __name__ == "__main__":
    try:
        os_system = DrummyOS()
        os_system.run()
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
        sys.exit()