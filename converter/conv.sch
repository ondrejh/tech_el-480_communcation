EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:conv-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Q_NPN_BCE Q?
U 1 1 59DFCB56
P 5800 3200
F 0 "Q?" H 6100 3250 50  0000 R CNN
F 1 "BC337" H 6250 3150 50  0000 R CNN
F 2 "" H 6000 3300 50  0000 C CNN
F 3 "" H 5800 3200 50  0000 C CNN
	1    5800 3200
	1    0    0    -1  
$EndComp
$Comp
L Q_NPN_BCE Q?
U 1 1 59DFCBE2
P 5800 4800
F 0 "Q?" H 6100 4850 50  0000 R CNN
F 1 "BC337" H 6250 4750 50  0000 R CNN
F 2 "" H 6000 4900 50  0000 C CNN
F 3 "" H 5800 4800 50  0000 C CNN
	1    5800 4800
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 59DFCCC9
P 5900 5300
F 0 "#PWR?" H 5900 5050 50  0001 C CNN
F 1 "GND" H 5900 5150 50  0000 C CNN
F 2 "" H 5900 5300 50  0000 C CNN
F 3 "" H 5900 5300 50  0000 C CNN
	1    5900 5300
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 59DFCCF3
P 5900 3700
F 0 "#PWR?" H 5900 3450 50  0001 C CNN
F 1 "GND" H 5900 3550 50  0000 C CNN
F 2 "" H 5900 3700 50  0000 C CNN
F 3 "" H 5900 3700 50  0000 C CNN
	1    5900 3700
	1    0    0    -1  
$EndComp
$Comp
L CONN_01X06 P?
U 1 1 59DFCD0E
P 3700 3750
F 0 "P?" H 3700 4100 50  0000 C CNN
F 1 "CONN_01X06" V 3800 3750 50  0000 C CNN
F 2 "" H 3700 3750 50  0000 C CNN
F 3 "" H 3700 3750 50  0000 C CNN
	1    3700 3750
	-1   0    0    -1  
$EndComp
Wire Wire Line
	3900 3500 4000 3500
Wire Wire Line
	4000 3500 4000 3200
Wire Wire Line
	4000 3200 4900 3200
$Comp
L R_Small R?
U 1 1 59DFCE4A
P 5000 3200
F 0 "R?" V 4900 3150 50  0000 L CNN
F 1 "82k" V 5100 3100 50  0000 L CNN
F 2 "" H 5000 3200 50  0000 C CNN
F 3 "" H 5000 3200 50  0000 C CNN
	1    5000 3200
	0    1    1    0   
$EndComp
$Comp
L R_Small R?
U 1 1 59DFCEBD
P 5500 3400
F 0 "R?" H 5600 3350 50  0000 L CNN
F 1 "27k" H 5600 3450 50  0000 L CNN
F 2 "" H 5500 3400 50  0000 C CNN
F 3 "" H 5500 3400 50  0000 C CNN
	1    5500 3400
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR?
U 1 1 59DFCF15
P 5500 3700
F 0 "#PWR?" H 5500 3450 50  0001 C CNN
F 1 "GND" H 5500 3550 50  0000 C CNN
F 2 "" H 5500 3700 50  0000 C CNN
F 3 "" H 5500 3700 50  0000 C CNN
	1    5500 3700
	1    0    0    -1  
$EndComp
Wire Wire Line
	5500 3500 5500 3700
Wire Wire Line
	5900 3700 5900 3400
Wire Wire Line
	5100 3200 5600 3200
Wire Wire Line
	5500 3300 5500 3200
Connection ~ 5500 3200
Wire Wire Line
	3900 3600 5500 3600
Connection ~ 5500 3600
Wire Wire Line
	3900 3700 4000 3700
Wire Wire Line
	4000 3700 4000 4800
Wire Wire Line
	4000 4800 4900 4800
$Comp
L R_Small R?
U 1 1 59DFD0A1
P 5000 4800
F 0 "R?" V 4900 4750 50  0000 L CNN
F 1 "82k" V 5100 4700 50  0000 L CNN
F 2 "" H 5000 4800 50  0000 C CNN
F 3 "" H 5000 4800 50  0000 C CNN
	1    5000 4800
	0    1    1    0   
$EndComp
Wire Wire Line
	5100 4800 5600 4800
$Comp
L R_Small R?
U 1 1 59DFD13E
P 5500 5000
F 0 "R?" H 5600 4950 50  0000 L CNN
F 1 "27k" H 5600 5050 50  0000 L CNN
F 2 "" H 5500 5000 50  0000 C CNN
F 3 "" H 5500 5000 50  0000 C CNN
	1    5500 5000
	-1   0    0    1   
$EndComp
$Comp
L GND #PWR?
U 1 1 59DFD223
P 5500 5300
F 0 "#PWR?" H 5500 5050 50  0001 C CNN
F 1 "GND" H 5500 5150 50  0000 C CNN
F 2 "" H 5500 5300 50  0000 C CNN
F 3 "" H 5500 5300 50  0000 C CNN
	1    5500 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	5500 5100 5500 5300
Wire Wire Line
	5500 4900 5500 4800
Connection ~ 5500 4800
Wire Wire Line
	5900 5300 5900 5000
Text GLabel 7100 5200 2    60   Input ~ 0
GND
Wire Wire Line
	5900 5200 7100 5200
Connection ~ 5900 5200
Wire Wire Line
	5900 4600 5900 4500
Wire Wire Line
	5900 4500 7100 4500
Text GLabel 7100 4500 2    60   Input ~ 0
UART1
Text GLabel 7100 2900 2    60   Input ~ 0
UART2
Wire Wire Line
	5900 3000 5900 2900
Wire Wire Line
	5900 2900 7100 2900
Text GLabel 7100 2200 2    60   Input ~ 0
VCC
$Comp
L R_Small R?
U 1 1 59DFD450
P 6900 2700
F 0 "R?" H 7000 2650 50  0000 L CNN
F 1 "3k3" H 7000 2750 50  0000 L CNN
F 2 "" H 6900 2700 50  0000 C CNN
F 3 "" H 6900 2700 50  0000 C CNN
	1    6900 2700
	-1   0    0    1   
$EndComp
Wire Wire Line
	6900 2600 6900 2200
Wire Wire Line
	6600 2200 7100 2200
Wire Wire Line
	6900 2800 6900 2900
Connection ~ 6900 2900
$Comp
L R_Small R?
U 1 1 59DFD556
P 6900 4300
F 0 "R?" H 7000 4250 50  0000 L CNN
F 1 "3k3" H 7000 4350 50  0000 L CNN
F 2 "" H 6900 4300 50  0000 C CNN
F 3 "" H 6900 4300 50  0000 C CNN
	1    6900 4300
	-1   0    0    1   
$EndComp
Wire Wire Line
	6900 4400 6900 4500
Connection ~ 6900 4500
Wire Wire Line
	6900 4200 6900 4100
Wire Wire Line
	6900 4100 6600 4100
Wire Wire Line
	6600 2200 6600 4750
Connection ~ 6900 2200
$Comp
L C_Small C?
U 1 1 59DFDC34
P 6600 4850
F 0 "C?" H 6700 4900 50  0000 L CNN
F 1 "100n" H 6700 4800 50  0000 L CNN
F 2 "" H 6600 4850 50  0000 C CNN
F 3 "" H 6600 4850 50  0000 C CNN
	1    6600 4850
	1    0    0    -1  
$EndComp
Connection ~ 6600 4100
Wire Wire Line
	6600 4950 6600 5200
Connection ~ 6600 5200
Text Label 4100 4750 0    60   ~ 0
BOILER
Text Label 4100 3150 0    60   ~ 0
ENET_MODULE
Text Notes 7550 4550 0    60   ~ 0
BOILER
Text Notes 7550 2950 0    60   ~ 0
ENET_MODULE
$EndSCHEMATC
