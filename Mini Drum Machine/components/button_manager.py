"""
--------------------------------------------------------------------------
Button Manager (Version 2: Bounds Checked)
--------------------------------------------------------------------------
"""
from threaded_input import ThreadedInput
import time

class ButtonManager:
    def __init__(self, left_pin="P2_28", right_pin="P2_30", select_pin="P2_32"):
        self.btn_left   = ThreadedInput(left_pin, label="Left")
        self.btn_right  = ThreadedInput(right_pin, label="Right")
        self.btn_select = ThreadedInput(select_pin, label="Select")
        
        self.menu_index = 0
        self.min_index  = 0
        self.max_index  = 0 # Start at 0, DrummyOS will update this per state

    def start(self):
        # We start the background threads
        self.btn_left.start(on_press=self._on_left_click)
        self.btn_right.start(on_press=self._on_right_click)
        # Start select - ensures the thread is running to catch is_pressed()
        self.btn_select.start() 

    def reset_index(self, max_val, start_val=0):
        """Call this whenever you change states (e.g., entering Browser)"""
        self.menu_index = start_val
        self.max_index = max_val

    def _on_left_click(self):
        if self.menu_index > self.min_index:
            self.menu_index -= 1
        else:
            # OPTIONAL: Wrap around to the end
            self.menu_index = self.max_index

    def _on_right_click(self):
        if self.menu_index < self.max_index:
            self.menu_index += 1
        else:
            # OPTIONAL: Wrap around to the beginning
            self.menu_index = self.min_index

    def stop(self):
        self.btn_left.stop()
        self.btn_right.stop()
        self.btn_select.stop()