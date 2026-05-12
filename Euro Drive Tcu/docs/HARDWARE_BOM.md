# Hardware BOM

## Shop Computer

- Windows laptop or rugged tablet
- VS Code
- Python 3.10 or newer
- USB isolation recommended for bench work

## Vehicle / Bench Interfaces

- SAE J2534 pass-thru interface for authorized programming workflows
- CAN/CAN FD USB interface for read-only logging and development
- Examples to evaluate:
  - PEAK PCAN-USB FD
  - Kvaser CAN/CAN FD interface
  - Vector VN-series interface

## Power

- 12-14.5 V bench power supply, 30-60 A preferred
- Automotive battery support unit for in-car sessions
- Fused power distribution
- Emergency stop
- Digital multimeter
- Oscilloscope or logic analyzer

## Harnessing

- OBD-II J1962 cable
- DQ250 bench adapter
- DQ381 bench adapter
- DQ500 bench adapter
- DL501 bench adapter
- Inline fuse carrier
- Ignition simulation switch
- Switchable 120 ohm CAN termination
- Harness labels with family, revision, date, and pinout source

## Custom Interface PCB Blocks

- Automotive microcontroller with CAN FD
- Dual CAN/CAN FD transceivers
- Optional LIN transceiver
- Galvanic isolation
- USB-C or USB-B connector
- Reverse-polarity protection
- Load dump and transient suppression
- ESD protection
- Common-mode choke for CAN
- Buck regulators for 5 V and 3.3 V
- Voltage measurement
- Current measurement
- Hardware write-enable switch, normally disabled
- Emergency stop input
- Status LEDs
- Rugged enclosure and keyed connectors

## Verification

- Confirm pinout from licensed service data
- Confirm bus voltage and termination before connecting a TCU
- Confirm current limit before bench power-up
- Log baseline communication before running repeated tests
