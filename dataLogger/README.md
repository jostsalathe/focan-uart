# Data Logger

This is a small PCB for logging and manipulating the communication between the display and the motor controller.

## Features

* microSD card slot
  * saving logs (one file per power cycle / ride)
  * configuration file
* 2 * JST SM 5 pin connections one male and one female for communication to/from display and motor controller
* Microcontroller ESP32
  * WiFi for configuration, internet time and accessing log files
  * SPI for SD card
  * 2 spare UARTs for communication to/from display and motor controller
  * RTC for accurate time stamps in file name and log entries
