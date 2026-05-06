<h1>RF Transponder - With GPS and RF functionality</h1>

**Author:** Alejandro Andrade-Risco and AVIO R&D
**Special Thanks to:** Deepak Narayan and Erik Welsh

<h2> Goal </h2>
The purpose of this project was to create the first iteration of an in-house RF PCB board that could be used for Rice ECLIPSE rockets to gain communication and GPS functionality. Thus, this PCB includes the schematics, layout and parts for a transponder that can be placed inside the rocket to communicate with a satellite to track GPS position and to communicate with a ground station where operators can maintain connection with the rocket.

<h2> PCB Description </h2>
The PCB itself is of intermediate to high level difficulty mostly because of the complexity of the RF and power traces which vary in width and required impedance matching. I will be breaking down the main sections of the PCB so that the purpose of the components is well understood in case it wants to be replicated.

<h3> JST 12-pin Connector </h3>
The JST 12-pin Connector is what we use to connect to our flight computer board which has the microcontroller that controls our board. Thus, make no mistake this board requires a microcontroller to operate (flight computer uses an RP-2350), it's just that in our case it's not on our board it's on a separate board that will be stacked with ours in the rocket. The connections of this 12-pin connector include GPIO, SPI, CS, power

<h3> CC1200 - Transmitter </h3>
The CC1200 is simply the main transmitter, the RF backend, and it mainly connects to the JST 12-pin connector and the RF Filter which itself connects to the CC1190 (talked about later). Some important things to know are the following. 
- The pins with resistors before the JST connects with the CC1200 are simply used as test points to test the signal
- There is a reset button that allows for resetting the CC1200
- There is a long chain of decoupling capacitors that are simply used for power filtering, especially useful since we have RF traces and components that need as little noise as possible
- The power going to the CC1200 goes through a small power filter with a ferrite bead before getting the CC1200
- There are also header pins to test the GND and power of the CC1200
- Only RF traces go into the RF Filter
- There is a 32 MHz crystal oscillator just connect it as shown
- In terms of PCB Layout, vias are especially useful to make traces work and to connect to the power and ground layers easily rather than individually connecting everything.

<h3> RF Filter </h3>
The RF filter is important as we're dealing with RF traces that are very sensitive and we have enough link budget to have this, we originally also wanted a SAW filter but that dug too much into link budget. This RF filter is the intermediate connection between the CC1200 and CC1190, and after the RF trace passes through the RF filter we put a coupler to then connect to a SMA port that allows us to probe the signal to see if anything messes up before getting to the CC1190. The RF filter is also crucial because it allows us to turn 4 RF traces into just 1 RF trace.

<h3> CC1190 </h3>
