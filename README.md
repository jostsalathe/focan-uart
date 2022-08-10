# focan-uart

Reverse engineering effort for the UART protocol used between Focan E-Scooter/-Bike displays (GZ3 is the actual test subject) and motor controllers.


## physical interface

The pinout of the connectors can be acquired from the *DU*s [user manual](./doc/2022-06-29%20Focan%20GZ-3%20user%20manual.pdf) and here are some additional details I deduced with the help of a multimeter and an oscilloscope:

| Pin # | Wire color | Function | Driven by | note |
| --- | --- | --- | --- | --- |
| 1 | red | battery voltage | *MCU* | *DU* draws about 11 mA when *MCU* is disconnected and 40 mA during normal operation (without lights). |
| 2 | blue | controller power | *DU* | This supplies power to the *MCU* including lights. *MCU* without lights draws about 29 mA during normal operation. |
| 3 | black | ground | *common* | Swapping this wire with #2 kills the *DU*. Ask me how I know. |
| 4 | green | UART RX | *MCU* to 0~3.32 V |  |
| 5 | yellow | UART TX | *DU* to 0~3.48 V | *MCU* connects 5k6 pullup from 5 V when `controller power` is supplied by *DU* |


## protocol analysis

The protocol analysis and documentation can be found in [./protocolAnalysis/README.md](./protocolAnalysis/README.md).
