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
