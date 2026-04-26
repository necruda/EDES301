<h1>Mini Drum Machine</h1>

Author: Alejandro Andrade-Risco

Hackster.io Link: https://www.hackster.io/aa338/edes-301-mini-drum-b5fde8

<h2>Building Software Instructions</h2>

<h3>Threaded Digital Input Driver (threaded_input.py)</h3>

Summary
This file contains a single class, ThreadedInput, which serves as the low-level digital input driver for every physical button and touch pad in the project. It is the foundation that all other input managers (button_manager.py and pad_manager.py) are built on top of. Every physical button or pad gets its own ThreadedInput instance.

Class: ThreadedInput

This class monitors a single GPIO pin on a dedicated background thread, allowing the main program loop to continue running without being blocked waiting for button presses. It handles debouncing, edge detection, callback execution, and click latching.

Constructor parameters:

pin — the GPIO pin string to monitor (e.g. "P2_28")
label — a human readable name used for print statements and error messages
debounce_ms — how long in milliseconds to wait after a press before listening again, defaulting to 50ms. Buttons use 50ms and touch pads use 20ms for faster response

Key methods:

start(on_press, on_release) — begins the background monitoring thread and optionally binds callback functions to press and release events
stop() — signals the background thread to stop running
is_pressed() — returns the real-time hardware state of the pin, True if currently held down
was_clicked() — returns True only once per press using a latch mechanism, then resets itself. This is the preferred method for buttons in the main loop to prevent a single press from registering multiple times across loop iterations

Internal behavior:

The monitor thread polls at 100Hz (every 10ms)
It detects a press on a falling edge (HIGH to LOW) and a release on a rising edge (LOW to HIGH)
On a falling edge it sets an internal _was_clicked flag and fires the on_press callback if one is bound
On a rising edge it fires the on_release callback if one is bound
The thread starts with a 100ms startup delay to allow the GPIO pin to settle before monitoring begins

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
