# Adapter board for using the original Focan GZ3 Display for controlling a VESC6 motor controller

This project uses the UART interface of the VESC6 to translate the commands from the display unit to control and config commands for the VESC6 and extract motor status data from it to report sensible data back to the display unit.

The adapter also has to incorporate power distribution to the vehicle lighting as well as evaluation circuitry and logic for the break lever switches to cut power when breaks are applied (maybe even gradually apply regen?).

## shutting down the ESC

The display unit has a return path for the battery voltage which it switches on when it is turned on. This can be loaded with a few hundred mA. It originally enabled the motor controller and supplied the lights. But motor current would not run through this detour path.

The VESC6 has no enable input so we need a power switch to shut it off when the enable signal from the display unit is off. I started work on implementing a high side switch with a P channel MOSFET (turns out, one wouldn't be enough to dissipate the RDSon losses, two to four would be better).

I then realized by sheer luck through this [blog post](https://civilpedia.org/p/?t=Adding-Shutdown-to-VESC-6&pid=381) that the voltage supply on the VESC6 utilizes the buck converter that is integrated into the DRV8301 MOSFET driver IC to feed all the logic voltages. That IC has an enable pin for that buck converter that is unconnected (pulled high through internal pullup) on the VESC6 board.

When I pull that pin low, the whole VESC6 board only draws 0.74 mA @ 30 V. And the adapter board will also be supplied by this buck converter, so would draw nothing when disabled.

The approach in the aforementioned blog post should be suitable to our application as well. I have some 3V Zener diodes in stock. I measured the pullup current out of the Buck_En pin to be about 1.1 uA so 150k resistors should be plenty small to reliably pull the pin low whilst not wasting energy.


