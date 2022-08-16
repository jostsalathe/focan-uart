# Perfboard Prototype

## Used Parts

* ESP32-WROOM-32D module (U2)
* SPI MicroSD card module (J_SD1)
* DM01 V2.0 fixed voltabe buck converter module (52 V max input, 3.3 V out) (U1)
* 70 mm * 30 mm perforated prototyping board
* 470k 1% axial 1/4 W resistor (R2), 12k 1% 0603 1/10W SMD resistor (R3) and 100nF 0603 SMD capacitor (C1) for measuring battery voltage
* 10k 1% axial 1/4 W resistor (R4) and some 3V zener diode (D1) for wakeup pin
* 10k 1% axial 1/4 W resistor for EN pin pullup (R1)
* JST-SM 5 pin connectors, one of each gender (J_DU1 and J_MCU1)
* 5 pin socket for flashing firmware and debugging (J_PRG1)


## Pinout

| connector | pin# | signal name | ESP32 pin | description |
| --- | --- | --- | --- | --- |
| J_PRG1 | 1 | GND | GND | ground connection of programmer |
| J_PRG1 | 2 | TX_DBG | IO1 | UART TX to programmer |
| J_PRG1 | 3 | RX_DBG | IO3 | UART RX from programmer |
| J_PRG1 | 4 | BOOT | IO0 | boot mode with internal pullup |
| J_PRG1 | 5 | EN | EN | enable with external pullup (R1) |
| J_DU1/J_MCU1 | 1 | +BATT | IO39 | battery voltage that supplies this unit |
| J_DU1/J_MCU1 | 2 | PWR_MCU | IO34 | The DU feeds battery power to the MCU via this connection when it is on. Use this signal to wake from deep sleep. |
| J_DU1/J_MCU1 | 3 | GND | GND | ground connection for external hardware |
| J_DU1 | 4 | TX1 | IO17 | UART TX to DU |
| J_DU1 | 5 | RX1 | IO16 | UART RX from DU |
| J_MCU1 | 4 | RX2 | IO19 | UART RX from MCU |
| J_MCU1 | 5 | TX2 | IO18 | UART TX to MCU |
| J_SD1 | 1 | 3V3 | VDD | supply voltage for MicroSD card |
| J_SD1 | 2 | CS | IO32 | chip select for MicroSD card |
| J_SD1 | 3 | MOSI | IO33 | serial data to MicroSD card |
| J_SD1 | 4 | CLK | IO26 | serial clock for MicroSD card |
| J_SD1 | 5 | MISO | IO14 | serial data from MicroSD card |
| J_SD1 | 6 | GND | GND | ground conneciton for MicroSD card |


### Notes on Measuring +BATT

Due to the chosen voltage devider you should call `analogSetAttenuation(ADC_2_5db);`.

With this attenuation setting you should use `double vBat = (analogRead(39) + 272.5) / 77.95;` to calculate the actual battery voltage.
