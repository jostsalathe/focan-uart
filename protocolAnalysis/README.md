# High Level Analyzer for Saleae Logic 2

The protocol is analyzed by capturing the communication with a logic analyzer and looking for patterns. Any gained knowledge is then put into high level analyzer plugins (*HLA*) for that logic analyzer. This enables ongoing verification of previous insights.

![Schnueffelstueck](./doc/2022-06-10%20schnueffelstueck.jpg)

There is one HLA each for the UART signal between the display unit (*DU*) and the motor control unit (*MCU*):

* `FocanGZ3-TX`: *DU* -> *MCU*
* `FocanGZ3-RX`: *MCU* -> *DU*

## General protocol description

The communication uses full duplex UART at `TODO` V logic level running at 9600 baud.

The pinout can be acquired from the *DU*s [user manual](./doc/2022-06-29%20Focan%20GZ-3%20user%20manual.pdf).

As long as the *DU* is turned on, it will send a data frame to the *MCU* via the TX signal roughly every 0.1 seconds. The *MCU* will then reply to that via the RX signal.

## TX data frame

Each TX data frame consists of 20 bytes describing the whole configuration and state of the *DU*.

| offset | mask | name | description |
| --- | --- | --- | --- |
| 0x00 | 0xFF | device address (?) | seems to be always 1 in TX direction |
| 0x01 | 0xFF | data frame length | always 20  (0x14) in TX direction |
| 0x02 | 0xFF | protocol revision (?) | seems to be always 1 in both directions |
| *0x03* | *0xFC* | *unknown* |  |
| 0x03 | 0x03 | drive mode | 0: pedal drive, 1: electric drive, 2: both (set with P10) |
| *0x04* | *0xF0* | *unknown* |  |
| 0x04 | 0x0C | gear | 0: off, 1: eco, 2: mid, 3: high |
| 0x04 | 0x03 | gear again | repeated for some reason ¯\\\_(ツ)\_/¯ |
| *0x05* | *0x80* | *unknown* |  |
| 0x05 | 0x40 | kick start | 0: motor can start from still stand, 1: motor must turn before it can start (set with P09) |
| 0x05 | 0x20 | light enable | 0: light off, 1: light on |
| *0x05* | *0x1F* | *unknown* |  |
| 0x06 | 0xFF | number of speed magnets | ranging from 0 to 255 (set with P07) |
| *0x07* | *0xFE* | *unknown* |  |
| 0x07 | 0x01 | wheel diameter high | high byte of the following |
| 0x08 | 0xFF | wheel diameter low | in 1/10 inch ranging from 25 to 500 (set with P06) |
| *0x09* | *0xE0* | *unknown* |  |
| 0x09 | 0x1F | boost sensitivity | ranging from 1 to 24 (set with P11) |
| *0x0A* | *0xF8* | *unknown* |  |
| 0x0A | 0x07 | boost start strength | ranging from 0 to 5 (set with P12) |
| *0x0B* | *0xFF* | *unknown* |  |
| *0x0C* | *0x80* | *unknown* |  |
| 0x0C | 0x7F | speed limit | in km/h ranging from 0 to 100 (set with P08) |
| *0x0D* | *0xE0* | *unknown* |  |
| 0x0D | 0x1F | current limit | in A ranging from 1 to 20 (set with P14) |
| *0x0E* | *0xFC* | *unknown* | (maybe belonging to the following) |
| 0x0E | 0x03 | undervolt threshold high | high byte of the following |
| 0x0F | 0xFF | undervolt threshold low | in 1/10 volt (combination of P03 (range: 24V/36V/48V) and P15 (decivolt adjustment) |
| *0x10* | *0xFC* | *unknown* |  |
| 0x10 | 0x03 | speed lever position high | high byte of the following |
| 0x11 | 0xFF | speed lever position low | ranging from 0 to 1000 |
| *0x12* | *0x80* | *unknown* |  |
| 0x12 | 0x40 | cruise enable | (set with P17) |
| *0x12* | *0x30* | *unknown* |  |
| 0x12 | 0x0F | power magnetic steel disc type | 5/8/12 (set with P13) |
| 0x13 | 0xFF | CRC | check sum |

The CRC sum is calculated with the following algorithm parameters determined by the program [reveng](https://reveng.sourceforge.io/readme.htm) using captured samples:

`width=8  poly=0x01  init=0x00  refin=false  refout=false  xorout=0x00  check=0x31  residue=0x00  name=(none)`

## RX data frame

Each RX data frame consists of 14 bytes describing the state of the *MCU*.

| offset | mask | name | description |
| --- | --- | --- | --- |
| 0x00 | 0xFF | device address (?) | seems to be always 2 in RX direction |
| 0x01 | 0xFF | data frame length | always 14 (0x0E) in RX direction |
| 0x02 | 0xFF | protocol revision (?) | seems to be always 1 in both directions |
| *0x03* | *0xFF* | *unknown* |  |
| *0x04* | *0xFF* | *unknown* |  |
| *0x05* | *0xFF* | *unknown* |  |
| *0x06* | *0xFF* | *unknown* |  |
| *0x07* | *0xFF* | *unknown* |  |
| *0x08* | *0x80* | *unknown* |  |
| 0x08 | 0x7F | wheel speed high | high byte of the following |
| 0x09 | 0xFF | wheel speed low | in milliseconds/revolution ranging from 0 to 31456 |
| *0x0A* | *0xFF* | *unknown* |  |
| *0x0B* | *0xFF* | *unknown* |  |
| *0x0C* | *0xFF* | *unknown* |  |
| 0x0D | 0xFF | CRC | check sum |

The vehicle velocity `v[km/h]` can be calculated from the wheel speed `t[ms]` using the known wheel diameter `D[in]` like this:

```
perimeter P[m] = 0.0254 m/in * D * PI

v = 1000 ms/s * 3600 s/h * 0.001 km/m * P / t
v = 3600 * P / t
v = 3600 * 0.0254 * D * PI / t
v = 91.44 * PI * D / t
```

The CRC sum uses the same algorithm as TX direction.
