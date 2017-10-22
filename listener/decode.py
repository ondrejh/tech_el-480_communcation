#!/usr/bin/env python3

tech_dict = {
    0x01F6: 'Zadana teplota CO',
    0x01F9: 'Stav pokojoveho regulátoru (0/1)',
    0x0218: 'Konec rámce',
    0x0225: 'Zrušení alarmu',
    0x0226: 'Začátek rámce',
    0x028E: 'Zadaná teplota TUV',
    #0x0298: '',
    #0x0299: '',
    0x02F7: 'Nastavení ventilu',
    0x02FC: 'Změna zadané teploty CO',
    #0x0367: '',
    0x157C: 'Stav regulátoru',
    0x157D: 'Teplota CO naměřená',
    0x157E: 'Teplota CO zadaná',
    #0x157F: '',
    0x15A7: 'Typ regulátoru',
    0x15AC: 'Otevření ventilu (%)',#Procent otwarcia zaworu
    0x15CD: 'Stav čerpadel 0-topení domu, 1-priorita bojleru, 2-paralerně, 3-léto',#Tryb pomp: 0-3 Grzanie domu,Priorytet bojlera,Pompy równolegle,Tryb letni
    0x1610: 'Standby (Pohotovostní režim)',#Standby (Tryb Czuwania)
    0x1614: 'Teplota ventilu',#Temperatura zaworu
    0x1616: 'Zadaná teplota TUV',#Temp. zadana CWU
    0x1620: 'Hodiny',#Godzina
    0x1621: 'Den v týdnu',#Dzień tygodnia: 0-6 niedziela-sobota
    0x1624: 'Typ ventilu (1-CO, 0-podlahový)',#Typ zaworu: 1-CO 0-podłogowy
    0x166E: 'Teplota TUV naměřená',#Temp. zmierzona CWU
    0x167F: 'Nastavení ventilu',#Ustawienie zaworu
    0x1681: 'Venkovní teplota',#Temp. zewnętrzna
    0x169E: 'Limity CO',#minMax CO: 23085[5A2D]=45-90=[2D-5A]
    0x169F: 'Limity TUV',#minMax CWU
    0x16C2: 'Adresa ventilu',#Adres zaworu
    0x16C3: 'Limity ventilu',#minMax zaworu: 25354=10-99, 14090=10-55
}

def decode_line(line):

    if type(line)==bytearray:
        sp = line.decode('ascii').strip()
    else:
        sp = line.strip()

    if len(sp) == 0:
        return None

    sp = sp.split(':')
    if len(sp) != 2:
        return None
    #hp = sp[0].split()
    #source = hp[1]
    #timestamp = hp[0]

    # test even data
    sp = sp[1].split()
    if len(sp) & 1 != 0:
        return None

    # test begin
    if (sp[0] != '0226') or (sp[1] != 'FFF4'):
        return None
    sp = sp[2:]

    # test end
    if sp[-2] != '0218':
        return None
    #crc = sp[-1]
    sp = sp[:-2]

    data = []
    for i in range(len(sp)//2):
        data.append((int(sp[i*2], 16), int(sp[i*2+1], 16)))

    return tuple(data)

for line in open('testfile.txt'):
    data = decode_line(line)
    if data is not None:
        if len(data)>0:
            print(data)
            for d in data:
                #print('{0:04X} ({0:04}) {1}'.format(d[0], d[1]))
                if d[0] in tech_dict.keys():
                    print('{} {}'.format(d[1],tech_dict[d[0]]))
