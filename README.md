# tech_el-480_communcation
Let's find out how TECH EL-480 controller communicates to the modules and how to get some data out of it.

## start point
Having a boiler equiped with TECH EL-480 I want to get the field data out of it. I want to add the values to my home automation system, let say MQTT and some DB to store it. I thought I buy profi module for the purpose, but I found out TECH ST-505 quite useless. But it's good start point to fetch some communication and to mimic it ...
The (only) resource I found: https://www.elektroda.pl/rtvforum/topic2689981.html

Signals measured. Found TX, GND and RX signal. Signal are supposed to be kinda RS232, inverted, 9k6, 8bit no parity 1.5stop. Let's make the convertor to standard levels first ...

![fetcher - idea](/fetcher_schematic.png)

Well, the schematic needs some improvements. One of the signals is inverted (probably the one comming from ethernet module). I'm solving it with "SW inverter" on the launchpad - not perfect. Don't belive the data comming form enet module.

Nevermind, I've writen simple mqtt client throwing data into broaker. Than I've build simple app to get those "raw" data and show it. It also highlights the changes. Here you are:

![spy app](/firstapp.png)

## Tiva LaunchPad connections

Converter (see the schematic above) to EK-LM4F120XL LaunchPad, firmware in `tiva/`:

| Converter | LaunchPad | Function |
|-----------|-----------|----------|
| UART1 (BOILER, RJ12 pin 3) | PB0 (U1RX) | shown as `U1`, green LED |
| UART2 (ENET_MODULE, RJ12 pin 1) | PD6 (U2RX) | shown as `U2`, red LED |
| GND (RJ12 pin 2) | GND | common ground |
| VCC | LaunchPad supply | pull-up supply for the transistors |

Output goes through the debug USB (UART0, 115200 8N1), which shows up as `/dev/ttyACM0` on Linux. Both inputs are 9600 8N1 and receive only, the sniffer can't transmit to the bus.

Update 2026-11-04: UART2 now goes straight to PD6. It used to go to PA3, with PA4 linked to PD6, through the "SW inverter" in `project.c`. That inverter was the reason for the bad `U2` data, so the note above about not believing the enet module data no longer applies. All frames in both directions now pass the CRC. The inverter code is still in the firmware, but PA3 and PA4 are no longer connected.
