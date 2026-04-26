"""
--------------------------------------------------------------------------
Screen Manager (Full Drummy 3000 Screen Package)
--------------------------------------------------------------------------
"""
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time

# Constants for alignment
LEFT, CENTER, RIGHT = 0, 1, 2

class ScreenManager:
    def __init__(self, width=128, height=64):
        self.width = int(width)
        self.height = int(height)
        
        # Flag to prevent concurrent drawing (Fixes the rotation/memory error)
        self.is_drawing = False
        
        # 1. Load Font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            self.font = ImageFont.load_default()

        # 2. HARDWARE RESET
        self.reset_pin = digitalio.DigitalInOut(board.P1_2)
        self.reset_pin.direction = digitalio.Direction.OUTPUT
        self.reset_pin.value = False
        time.sleep(0.1)
        self.reset_pin.value = True
        time.sleep(0.1)

        # 3. SPI SETUP
        self.spi = busio.SPI(board.SCLK, MOSI=board.MOSI)
        while not self.spi.try_lock():
            pass
        self.spi.configure(baudrate=1000000) 
        self.spi.unlock()

        self.dc_pin    = digitalio.DigitalInOut(board.P1_4)
        self.cs_pin    = digitalio.DigitalInOut(board.P1_6)

        # 4. INITIALIZE DISPLAY
        self.disp = adafruit_ssd1306.SSD1306_SPI(
            self.width, self.height, self.spi, self.dc_pin, self.reset_pin, self.cs_pin
        )
        
        self.disp.fill(0)
        self.disp.show()
        
        # 5. Canvas
        self.image = Image.new("1", (128, 64))
        self.draw  = ImageDraw.Draw(self.image)

    def clear(self):
        # Using 127/63 to stay strictly within the 128x64 buffer bounds
        self.draw.rectangle((0, 0, 127, 63), outline=0, fill=0)

    def display_show(self):
        # GATE: If we are already pushing a frame, skip this one to avoid memory corruption
        if self.is_drawing:
            return
            
        self.is_drawing = True
        try:
            self.disp.image(self.image)
            self.disp.show()
        except Exception as e:
            # Catching SPI lag instead of crashing the OS
            pass
        finally:
            self.is_drawing = False

    def set_brightness(self, level):
        level = max(40, min(int(level), 100))  # floor of 40 instead of 0
        contrast_val = int((level / 100.0) * 255)
        self.disp.contrast(contrast_val)

    def draw_text_aligned(self, text, y, justify=CENTER):
        try:
            w = self.draw.textlength(text, font=self.font)
        except:
            w, _ = self.draw.textsize(text, font=self.font)

        if justify == CENTER:
            x = (64) - (int(w) // 2)
        elif justify == RIGHT:
            x = 127 - int(w)
        else:
            x = 0
            
        safe_x = max(0, min(int(x), 126))
        safe_y = max(0, min(int(y), 62))
        self.draw.text((safe_x, safe_y), text, font=self.font, fill=255)

    def draw_hud(self, volume, brightness):
        self.set_brightness(brightness)
        self.draw.rectangle((1, 3, 4, 9), fill=255) 
        self.draw.polygon([(4, 3), (9, 0), (9, 12), (4, 9)], fill=255)
        v_str = str(int(volume)) if isinstance(volume, (int, float)) else str(volume)
        self.draw.text((13, 1), v_str, font=self.font, fill=255)

        cx, cy = 100, 6
        self.draw.ellipse((cx-2, cy-2, cx+2, cy+2), outline=255)
        self.draw.line((cx, cy-4, cx, cy-6), fill=255)
        self.draw.line((cx, cy+4, cx, cy+6), fill=255)
        self.draw.line((cx-4, cy, cx-6, cy), fill=255)
        self.draw.line((cx+4, cy, cx+6, cy), fill=255)
        
        b_val = str(int(brightness)) if isinstance(brightness, (int, float)) else str(brightness)
        try:
            bw = int(self.draw.textlength(b_val, font=self.font))
        except:
            bw, _ = self.draw.textsize(b_val, font=self.font)
        
        self.draw.text((max(0, 126 - bw), 1), b_val, font=self.font, fill=255)
        self.draw.line((0, 13, 127, 13), fill=255)

    def draw_splash_screen(self):
        self.clear()
        self.draw.ellipse((44, 15, 84, 25), outline=255)
        self.draw.line((44, 20, 44, 30), fill=255)
        self.draw.line((84, 20, 84, 30), fill=255)
        self.draw.ellipse((44, 25, 84, 35), outline=255)
        self.draw.polygon([(25, 5), (30, 8), (48, 18), (46, 21)], fill=255)
        self.draw.polygon([(103, 5), (98, 8), (80, 18), (82, 21)], fill=255)
        self.draw_text_aligned("DRUMMY 3000", 40, justify=CENTER)

    def draw_browser(self, project_list, active_idx, volume="--", brightness="--"):
        self.draw_hud(volume, brightness) 
        full_list = ["+ NEW PROJECT"] + project_list
        item_h, list_top, visible = 12, 16, 4
        start_idx = max(0, min(active_idx - 1, max(0, len(full_list) - visible)))
        
        for i in range(visible):
            idx = start_idx + i
            if idx < len(full_list):
                y_pos = list_top + (i * item_h)
                try:
                    name = str(full_list[idx]).replace("PROJECT_", "").replace(".json", "")
                except:
                    name = "UNKNOWN"
                if idx == active_idx:
                    self.draw.rectangle((2, y_pos, 124, y_pos + item_h - 1), fill=255)
                    self.draw.text((6, y_pos), f"> {name}", font=self.font, fill=0)
                else:
                    self.draw.text((6, y_pos), f"  {name}", font=self.font, fill=255)

        if len(full_list) > visible:
            self.draw.rectangle((125, list_top, 127, 62), outline=255)
            denom = max(1, len(full_list))
            bar_h = max(5, int((visible / denom) * (62 - list_top)))
            bar_y = int((active_idx / denom) * (62 - list_top - bar_h))
            self.draw.rectangle((125, list_top + bar_y, 127, list_top + bar_y + bar_h), fill=255)

    def draw_modal(self, title, message, options=["NO", "YES"], active_idx=0):
        self.draw.rectangle((10, 12, 118, 52), fill=0, outline=255)
        self.draw_text_aligned(title, 16, justify=CENTER)
        self.draw_text_aligned(message, 26, justify=CENTER)
        
        # Dynamically space buttons based on count
        num_options = len(options)
        spacing = 90 // num_options
        for i, opt in enumerate(options):
            x_pos = 15 + (i * spacing)
            if i == active_idx:
                self.draw.rectangle((x_pos, 40, x_pos + 28, 50), fill=255)
                self.draw.text((x_pos + 2, 40), opt[:4], font=self.font, fill=0)
            else:
                self.draw.text((x_pos + 2, 40), opt[:4], font=self.font, fill=255)

    def draw_tempo_modal(self, bpm, active_idx=1):
        self.clear() 
        self.draw.rectangle((5, 10, 123, 54), outline=255, fill=0)
        self.draw_text_aligned("SET TEMPO (BPM)", 15, justify=CENTER)
        if active_idx == 0:
            self.draw.rectangle((10, 38, 45, 48), fill=255)
            self.draw.text((12, 38), "BACK", font=self.font, fill=0)
        else:
            self.draw.text((12, 38), "BACK", font=self.font, fill=255)
        
        start_x = 44
        self.draw.rectangle((start_x, 42, start_x + 40, 44), outline=255)
        fill_w = int(((bpm - 40) / 140.0) * 40)
        fill_w = max(0, min(fill_w, 40))
        self.draw.rectangle((start_x, 42, start_x + fill_w, 44), fill=255)
        
        bpm_text = f"{bpm}"
        if active_idx == 1:
            self.draw.rectangle((54, 30, 74, 40), fill=255)
            self.draw.text((56, 30), bpm_text, font=self.font, fill=0)
        else:
            self.draw.text((56, 30), bpm_text, font=self.font, fill=255)
        
        if active_idx == 2:
            self.draw.rectangle((95, 38, 115, 48), fill=255)
            self.draw.text((100, 38), "OK", font=self.font, fill=0)
        else:
            self.draw.text((100, 38), "OK", font=self.font, fill=255)

    def draw_sequencer_grid(self, step_data, cursor_step, playhead_step):
        row_h, start_y, label_w = 11, 17, 12 
        # Integer division to ensure coordinates stay on pixel boundaries
        step_w = (127 - label_w) // 32
        
        play_x = label_w + (int(playhead_step) * step_w)
        self.draw.line((play_x, start_y, play_x, start_y + 33), fill=255)
        
        curs_x = label_w + (int(cursor_step) * step_w)
        self.draw.line((curs_x, start_y - 2, curs_x, start_y), fill=255)
        
        labels = ["K", "S", "H"]
        for i in range(3): 
            y_off = start_y + (i * row_h)
            self.draw.text((2, y_off + 1), labels[i], font=self.font, fill=255)
            self.draw.rectangle((label_w, y_off, 126, y_off + row_h), outline=255)
            if i < len(step_data):
                for hit_step in step_data[i]:
                    x_pos = label_w + (int(hit_step) * step_w)
                    self.draw.rectangle((x_pos + 1, y_off + 2, x_pos + 3, y_off + row_h - 2), fill=255)

    def draw_footer_carousel(self, buttons, active_idx):
        self.draw.rectangle((0, 50, 127, 63), fill=0) 
        self.draw.line((0, 50, 127, 50), fill=255)
        sh_map = {"RECORD": "REC", "TEMPO": "BPM", "STOP": "STOP", "CLEAR": "CLR", "EXIT": "EXT", "SAVE": "SAVE", "PLAY": "PLAY"}
        start_btn = (int(active_idx) // 3) * 3
        for i in range(3):
            btn_idx = start_btn + i
            if btn_idx < len(buttons):
                x_pos = (i * 42) + 1
                name = sh_map.get(buttons[btn_idx], buttons[btn_idx][:4])
                if btn_idx == active_idx:
                    self.draw.rectangle((x_pos, 52, x_pos + 40, 62), fill=255)
                    self.draw.text((x_pos + 4, 52), name, font=self.font, fill=0)
                else:
                    self.draw.text((x_pos + 4, 52), name, font=self.font, fill=255)