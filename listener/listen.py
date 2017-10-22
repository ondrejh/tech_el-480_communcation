#!/usr/bin/env python3

from serial import Serial

filename = 'testfile.txt'

with Serial("/dev/ttyACM0", 115200, timeout=0.001) as port:

    with open(filename, 'wb') as file:
        while (1):
            try:
                lines = port.readlines()
                for line in lines:
                    file.write(line)
                    sp = line.decode('ascii').strip()
                    if len(sp)>0:
                        print(sp)
            except:
                break
