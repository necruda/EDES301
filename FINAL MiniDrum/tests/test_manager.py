from button_manager import ButtonManager
import time

manager = ButtonManager()
manager.start()

try:
    while True:
        time.sleep(1) # Keeping the main thread alive
except KeyboardInterrupt:
    manager.stop()