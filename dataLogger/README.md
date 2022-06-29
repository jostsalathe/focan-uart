# Data Logger

This is will be a small PCB for logging the communication between the display and the motor controller.

## Features

* USB-C
  * Flashing firmware via DFU
  * Writing debug serial to USB host
  * Setting RTC from USB host (via slim CLI menu)
* microSD card slot
  * saving logs (one file per power cycle / ride)
  * configuration file
* 2 * JST SM 5 pin connections one male and one female for communication to/from display and motor controller
* Microcontroller (`STM32F103R[C...G]` would have all the desired hardware)
  * SDIO for SD card
  * 2 * UART for communication to/from display and motor controller
  * USB with DFU and virtual COM port capabilities
  * RTC for accurate time stamps in file name and log entries

## Bill Of Materials

| JLCPCB part # | Description |
| --- | --- |
| C8323 | STM32F103RCT6 |
| C111196 | SOFNG TF-15x15 microSD card slot |
| C165948 | HRO TYPE-C-31-M-12 USB-C female connector for USB 2.0 |
