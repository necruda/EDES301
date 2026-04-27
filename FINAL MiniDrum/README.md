<h1>Mini Drum Machine</h1>

Author: Alejandro Andrade-Risco

Hackster.io Link: https://www.hackster.io/aa338/edes-301-mini-drum-b5fde8

<h2>Building Software Instructions</h2>

<h3>Things to install before coding</h3>

- Python
- Adafruit_BBIO
- mplayer
- adafruit-circuitpython-ssd1306
- adafruit-blinka
- Pillow

<h3>Threaded Digital Input Driver (threaded_input.py)</h3>

**Contributions**

Erik Welsh - code is based on threaded_button.py
Gemini AI - helped account for edge cases and small user experience features like debouncing and click latching

**Summary**

This file contains a single class, ThreadedInput, which serves as the low-level digital input driver for every physical button and touch pad in the project. It is the foundation that all other input managers (button_manager.py and pad_manager.py) are built on top of. Every physical button or pad gets its own ThreadedInput instance.

**Class: ThreadedInput**

This class monitors a single GPIO pin on a dedicated background thread, allowing the main program loop to continue running without being blocked waiting for button presses. It handles debouncing, edge detection, callback execution, and click latching.

**Construction parameters:**

pin — the GPIO pin string to monitor (e.g. "P2_28")
label — a human readable name used for print statements and error messages
debounce_ms — how long in milliseconds to wait after a press before listening again, defaulting to 50ms. Buttons use 50ms and touch pads use 20ms for faster response

**Key functions:**

start(on_press, on_release) — begins the background monitoring thread and optionally binds callback functions to press and release events
stop() — signals the background thread to stop running
is_pressed() — returns the real-time hardware state of the pin, True if currently held down
was_clicked() — returns True only once per press using a latch mechanism, then resets itself. This is the preferred method for buttons in the main loop to prevent a single press from registering multiple times across loop iterations

**Internal behavior:**

The monitor thread polls at 100Hz (every 10ms)
It detects a press on a falling edge (HIGH to LOW) and a release on a rising edge (LOW to HIGH)
On a falling edge it sets an internal _was_clicked flag and fires the on_press callback if one is bound
On a rising edge it fires the on_release callback if one is bound
The thread starts with a 100ms startup delay to allow the GPIO pin to settle before monitoring begins

<h3>Button Manager (button_manager.py)</h3>

**Summary**

This file contains a single class, ButtonManager, which manages the three physical navigation buttons of the project. It wraps three ThreadedInput instances and translates left and right button presses into a single shared menu_index integer that the main program uses to navigate menus and carousels. This file depends directly on threaded_input.py and must have access to it.

**Class: ButtonManager**

This class abstracts the three navigation buttons into a simple index-based navigation system. The left and right buttons decrement and increment the index respectively, while the select button is left without a callback and is instead polled directly by the main loop using was_clicked().

**Construction parameters:**

left_pin — GPIO pin string for the left navigation button, defaults to "P2_28"
right_pin — GPIO pin string for the right navigation button, defaults to "P2_30"
select_pin — GPIO pin string for the select/confirm button, defaults to "P2_32"

**Key ideas:**

menu_index — the current navigation position, shared and read directly by the main program loop
min_index — always 0, the lower bound of navigation
max_index — the upper bound of navigation, updated by the main program each time the state changes to reflect how many items are in the current menu or carousel

**Key functions:**

start() — initializes all three background threads. Left and right are bound to their respective callbacks. Select is started with no callback since it is polled via was_clicked() in the main loop
stop() — stops all three background threads cleanly
reset_index(max_val, start_val) — resets menu_index to a given starting value and sets a new upper bound. Should be called whenever the program transitions to a new state with a different number of navigable items

**Navigation behavior:**

Left button decrements menu_index by 1. If already at the minimum it wraps around to max_index
Right button increments menu_index by 1. If already at the maximum it wraps around to min_index
The wrapping behavior means navigation is circular in both directions

<h3>Pad Manager (pad_manager.py)</h3>

**Contributions**

Gemini AI - helped figure out the default velocity for the touch sensors and came up with queue idea

**Summary**

This file contains a single class, PadManager, which manages the three touch capacitive sensors of the Mini Drum. Uses ThreadedInput instances, but is specifically designed for high-speed drum triggering rather than menu navigation. Instead of updating an index, it feeds incoming hits into a queue that the main program drains every loop iteration. This file depends directly on threaded_input.py and must have access to it.

**Class: PadManager**

This class abstracts the three drum pads into a hit queue system. Each pad runs on its own background thread listening for touches, and every hit is timestamped and stored in a queue until the main loop is ready to process it. 

**Construction parameters:**

kick_pin — GPIO pin string for the kick drum pad, defaults to "P2_19"
snare_pin — GPIO pin string for the snare drum pad, defaults to "P2_22"
hat_pin — GPIO pin string for the hi-hat pad, defaults to "P2_24"

**Key ideas:**

hit_queue — a list of tuples storing unprocessed hits. Each entry is (pad_name, velocity, timestamp) where pad_name is one of "KICK", "SNARE", or "HI-HAT"
default_velocity — set to 100 for all hits since touch pads do not measure pressure. This value is included in the queue tuple for forward compatibility if velocity sensitivity is ever added

**Key functions:**

start() — initializes all three background threads and binds each pad to the internal _register_hit callback using a lambda
stop() — stops all three background threads. This should be called explicitly on program exit, unlike the navigation buttons
get_new_hits() — the primary method called by the main loop each iteration. Returns a copy of all hits that have accumulated since the last call and clears the queue. Returns a list of (pad_name, velocity, timestamp) tuples
is_pad_pressed(pad_name) — returns True if the named pad is currently being touched. Useful for UI feedback if needed
_register_hit(pad_name) — internal callback fired by each ThreadedInput on a press event. Appends a hit tuple to the queue and prints a diagnostic symbol to the terminal

<h3>Potentiometer Manager (pot_manager.py)</h3>

**Contributions**

Erik Welsh - code is based on potentiometer.py
Gemini AI - helped with establishing discrete steps for the cursor, smoothing math, and tracking the most recent input changes in the dials

**Summary**

This file has one class, PotManager, which reads the three potentiometer knobs on the system. The three knobs control the timeline cursor position (playhead), the volume, and the screen brightness. It uses the PocketBeagle's built-in ADC to read the dials positions and applies some "smoothing" math so the values don't jump around all the time; this smoothing idea was AI-inspired.

**Class: PotManager**

This class reads three analog knobs and converts their raw ADC values into useful numbers for the rest of the program. It throttles how often it reads to avoid overwhelming the SPI bus that the screen is also using, and smooths the readings over time to keep things stable.

**Construction parameters:**

timeline_steps — how many discrete steps the timeline dial is divided into, defaults to 21 but set to 32 in the main program to match the 32 step sequencer grid

**Key ideas:**

pot_config — a dictionary mapping each knob's name to its ADC channel: TIMELINE on AIN0, VOLUME on AIN1, and BRIGHT on AIN2
values — a dictionary storing the current smoothed reading for each knob, initialized to 0.8 so the screen doesn't start at zero brightness before the first real reading comes in
smoothing — set to 0.15, meaning each new reading only nudges the stored value by 15% rather than replacing it entirely. Crucial so settings don't act up, like brightness and volume.
last_read_time — tracks when the last ADC read happened so readings are throttled to every 30ms

**Key methods:**

update() — should be called every main loop iteration. Reads all three ADC channels if 30ms has passed since the last read and updates the smoothed values
get_timeline_step() — converts the raw TIMELINE knob value into an integer step between 0 and timeline_steps - 1. This is what controls the playhead cursor position when the sequencer is stopped
get_volume_midi() — returns the VOLUME knob value as an integer from 0 to 100
get_brightness_percent() — returns the BRIGHT knob value as an integer from 0 to 100

<h3>Audio Manager (audio_manager.py)</h3>

**Contributions**

Gemini AI - Helped with figuring out how to sync the volume function to the sound without causing errors

**Summary**

This file has one class, AudioManager, which handles all sound playback for the project. It's pretty straightforward, when the main program tells it to play a sound, it launches an mplayer subprocess to play the corresponding .wav file. There are five sounds total: kick, snare, hi-hat, and two metronome sounds for the beat counter, however these can be changed to whatever is desired; just make sure to change the names.

**Class: AudioManager**

This class maps pad index numbers to audio sample files and plays them on demand by spawning mplayer as a background process. Each sound plays independently without blocking the main loop.

**Construction parameters:**

sample_folder — the absolute path to the folder containing all the .wav files, defaults to "/var/lib/cloud9/EDES301/MiniDrum/samples". If the folder doesn't exist at startup it prints a critical warning to the terminal.

**Key ideas:**

samples — a dictionary mapping integer indices to .wav filenames. Map how you like.

**Key methods:**

play_sample(pad_index, volume) — takes an integer index and an optional volume from 0 to 100, defaulting to 100. Looks up the corresponding filename, verifies it exists, and launches mplayer as a detached subprocess to play it. If the file is missing it prints a warning but doesn't crash. Volume is clamped between 0 and 100 before being passed to mplayer.

<h3>Project Manager (project_manager.py)</h3>

**Contributions**

Gemini AI - Helped figure out how automatically generate files when needed, and keep save data

**Summary**

This file has one class, ProjectManager, which handles saving, loading, and deleting projects. Each project is just a JSON file containing the grid data and BPM, stored in a dedicated projects folder on the PocketBeagle. It's a pretty simple file but it's what gives the drum machine the ability to remember what you've recorded between sessions.

**Class: ProjectManager**

This class reads and writes project files to a specified directory on disk. Each project is stored as a .json file containing two fields — the grid data and the BPM.

**Construction parameters:**

directory — the absolute path to the folder where project files are stored, defaults to "/var/lib/cloud9/...". If the folder doesn't exist at startup it gets created automatically.

**Key methods:**

get_project_list() — scans the projects folder and returns a list of project names with the .json extension stripped. This is what populates the browser screen
save(name, grid_data, bpm) — writes the grid and BPM to a JSON file named after the project. Projects are automatically named PROJECT_ followed by a Unix timestamp in drummy_os.py
load(name) — reads a project file and returns the grid data and BPM as a tuple. Returns None, None if the file doesn't exist
delete(name) — removes the project file from disk if it exists

**Important integration notes:**

File structure: Each saved project is a .json file with exactly two fields: bpm and grid
The grid field is a list of three lists, one per track, where each inner list contains the step indices where hits were recorded.
The projects folder must exist or be creatable at the path specified. On a rebuilt system the directory path in the Construction should be updated to match wherever the project files will be stored.

<h3>Screen Manager (screen_manager.py)</h3>

**Contributions** 

Erik Welsh - code is based on spi_screen.py
Gemini AI - exact graphic details needed for polygons

**Summary**

This file has one class, ScreenManager, which handles everything the user sees on the OLED display. It initializes the screen hardware over SPI, maintains a PIL image buffer that gets drawn to each frame, and provides a draw method for every screen in the program. All drawing happens on the buffer first and then the whole thing gets pushed to the physical display at once. This file is especially long, it would be a lot to go through every single function, thus, I thought to understand the main concepts was more important than getting a step-by-step process of how to do it. Not to mention there is more room for customization here compared to the other classes, as long as the concepts are similar the rest of the architecture should still mesh to make the final product.

**Class: ScreenManager**

This class owns the display hardware and exposes a set of draw methods the main program calls each loop iteration to build and push a frame to the screen.

**Initialization sequence:**

The Construction sets up five things in order: loads the DejaVu Sans font at size 10, performs a hardware reset by toggling the reset pin LOW then HIGH, sets up the SPI bus at a baudrate of 1,000,000, initializes the SSD1306 display driver, and creates the PIL image buffer and draw object that all draw methods write to.

**Core functions:**

clear() — fills the buffer with black. Must be called at the start of each frame or old pixels bleed through
display_show() — pushes the current buffer to the physical display. Has a gate flag that skips the push if one is already in progress to prevent SPI bus corruption
set_brightness(level) — sets display contrast with a minimum floor of 40 so the screen never goes completely dark

**Draw functions:**

There is one draw method per screen in the program — splash screen, browser, sequencer grid, tempo editor, modal popups, the HUD status bar, and the footer carousel. Each one draws its entire screen's worth of content to the PIL buffer using a combination of rectangles, lines, polygons, and text. The main program calls whichever one matches the current state each loop iteration, then calls display_show() to push it.

**Important integration note:**

Every screen in the program follows the same pattern: call clear(), call the relevant draw method(s), then call display_show(). The clear call is critical; skipping it would cause the previous frame's pixels to bleed into the new one.
display_show() is always called once at the very end of the main loop in "drummy_os.py" regardless of which state the program is in, this way individual draw methods never call it themselves.

<h3>Drummy OS (drummy_os.py)</h3>

**Contributions**

Gemini AI - Helped a lot with troubleshooting and coming up with exact numbers needed for loading and how to tie the screen manager with the drummy os which was the hardest part, as well as the sequencer engine as there is no quantization so this was more abstract than normal

**Summary**

This is the main file that ties the entire project together. It has one class, DrummyOS, which initializes all the hardware managers, runs the main loop, and contains the state machine that controls everything the user interacts with. This is the file you run to start the program. Every other file in the project exists to serve this one.

**Class: DrummyOS**

This class owns all the manager instances and runs a continuous loop that reads input, updates state, and renders the screen at roughly 50ms intervals. The program is structured as a state machine with five states that each have their own logic and screen.
The five states:
STATE_SPLASH — the boot screen, waits for select to be pressed to move to the browser
STATE_BROWSER — project selection screen where the user picks an existing project or starts a new one
STATE_SEQUENCER — the main drum machine screen where recording, playback, and live pad hitting all happen
STATE_MODAL — a popup confirmation screen used for CLEAR, EXIT, and project LOAD/DELETE actions
STATE_TEMPO — a dedicated screen for adjusting the BPM using the timeline dial

**Key state ideas and functions:**

grid_data — a list of three lists, one per track (kick, snare, hi-hat). Each inner list holds the step indices where hits have been recorded. This is the core data structure of the sequencer
is_playing and is_recording — boolean flags that control the playback and recording behavior of the sequencer engine
playhead — the current step position from 0 to 31. Syncs to the timeline dial when stopped, and advances automatically with BPM timing when playing
current_bpm — the tempo in beats per minute, defaults to 120, adjustable from 40 to 180 in the tempo screen
carousel — the list of action buttons shown in the sequencer footer: ["RECORD", "PLAY", "STOP", "TEMPO", "CLEAR", "SAVE", "EXIT"]

Sequencer engine — update_sequencer_engine():

This is the audio heart of the program. Every loop iteration in the sequencer state it does two things. First it drains the pad hit queue and plays any live hits immediately, recording them to grid_data at the current playhead position if recording is active. Second, if playback is active, it checks if enough time has passed based on the BPM to advance the playhead by one step, fire metronome clicks on every 8th step, and trigger any recorded hits at the current playhead position.

Action handling — handle_action():

RECORD — if not recording, starts recording and playback from the current dial position. If already recording, stops both recording and playback without resetting the playhead
PLAY — if not recording, starts playback from the current dial position without affecting recording state
STOP — if not recording, pauses playback without resetting the playhead
TEMPO — switches to the tempo state with the dial selector active
CLEAR and EXIT — both route through the modal confirmation state before executing
SAVE — immediately saves the current grid and BPM to a timestamped project file

Other state handlers:

Each state has a dedicated handler method. The browser handler manages project list navigation and routes to either a new empty sequencer or the load/delete modal. The modal handler handles both the 2-option CANCEL/OK modals and the 3-option BACK/DELETE/LOAD project modal. The tempo handler maps the timeline dial's 0-31 range to a BPM range of 40 to 180.

<h2>Operating Software Instructions</h2>

Operating the mini drum should be pretty intuitive as there is a whole program to go with it but here is some helpful starter information and also some specifics on how this basic mini drum actually works when you get to the sequencer.

**Buttons**

I had three buttons, a SELECT button, a RIGHT/UP button, and LEFT/DOWN button. Using these buttons you're able to navigate all the menus presented in the software.

**Potentiometers/Dials**

Also three dials, one dial controls the cursor/playhead on the sequencer and also a scale that pops up when on the tempo/BPM prompt box, another dial controls the volume of the sounds going through the audio output, and the last controls the brightness of the OLED SPI screen itself.

**CapacitiveTouchSensors**

There are also three touch sensors, these only control the specific samples that are installed in the samples library (currently labeled kick, snare, and crash).

**USB Port for Audio**

The USB port is the way to get audible sound. Simply connect your headphones or speaker through a standard 3.5mm audio jack cable and you're good to go.

**Step-by-step Program Operation Instructions**

1) Plug a micro usb cable between your computer and the pocketbeagle.

2) Go to cloud9, open a cloud9 terminal and cd into the folder holding the program in this case called MiniDrum.

3) in the terminal input: sudo python3 drummy_os.py

4) The terminal should say the drummy 3000 or something is booted, and on the screen a splash screen of a drum and sticks with a flashing start button prompt should pop up. (This is Screen 1)

5) Press the SELECT button

Side Note: From here on out you can change the volume or brightness when and as you place using the respective dials. The volume and brightness icons are found at the top of Screens 2 and 3, with a number next to it representing the magnitude of the respective setting based on the dials.

6) Now you should be on Screen 2 or the Browser screen, this works as a simple browsing system you can either make a New File or Open/Delete an exisiting file on the pocket beagle. Navigate this menu using the up and down buttons (or left/ and right) to hover onto a screen button and select that screen button using the select button. a) If you choose the New File it won't prompt anything and just open a new project going to Screen 3. b) If you select an old file it will prompt you with 3 screen buttons (back, del, load) select accordingly.

7) Assuming you either clicked New File or Load, you will be taken to Screen 3, the sequencer screen. There is a lot of information to be processed here so let's start from the bottom: the carousel of screen buttons.

I needed to put a lot of functionality into this screen so that it actually worked like a basic drum machine, the solution, a carousel of screen buttons that the user can scroll through depending on their need.

REC: Record whatever you play on the touch sensors, it will be over dubbed on an audio and json file that contains the graphical/text and audio information of your touches (so like what those touches mean). In general think of it as your "editor" state button for making loops. If you're already recording and you select the REC button again, it will stop the recording. Also a metronome at the tempo specified by the user will always play during a recording session in the background, its sound isn't actually registered onto the audio file, the number is though.

PLAY: Different from recording, play simply plays what you currently have on your loop file, so if you've recorded anything it will start wherever your cursor or playhead is at the time and play sounds from there based on the file.

STOP: Pause whatever you're playing at that moment and wherever the playhead is currenlty located at time wise, ;this does not work to pause a recording.

BPM: This button is meant to allow the user to edit the built in metronome (it's always on, I haven't built in an option to turn it off). When selected a prompt pops up with a number scale and a BACK button on the left and an OK button on the right. Use the left and right buttons to navigate the prompt, if you are hovering on the scale and then you select it with the SELECT button, you can then use the cursor dial to adjust the BPM or tempo of the metronome.

CLR: When selected it will prompt you with "Are you sure?" if you press OK it will clear the data recorded onto the file, letting you restart with ease. If you press back you simply go back to the sequencer.

SAVE: Save your file and your work by clicking save and overwriting your data.

EXIT: When selected it will prompt the same "Are you sure?" prompt as the CLR, though if you press OK it will return you to Screen 2, the browser screen.

Now then, lets move on to the main entree, the sequencer itself. In the middle of the screen you will see three rows divided in blocks of 32 each, Allowing you to register 32 sounds per row, each row corresponds to one touch sensor or sample. The blocks that you see in the rows represent your touch, so when the playhead goes over it, it will play the sound registered on that row at the time specified by the block. Right now I have the "kick" as the top row, "snare" as middle row, "crash" at bottom row.

And that's all of the programs functionality so far.
