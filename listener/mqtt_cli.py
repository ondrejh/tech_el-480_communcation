#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *

from lxml.etree import parse, Element, SubElement, Comment, tostring

from threading import Thread

from time import sleep

import paho.mqtt.client as mqtt
from decode import decode_raw, frame_valid, frame_keys

MQTT_SERVER_IP = "192.168.1.200"
MQTT_SERVER_PORT = 1883
MQTT_USER_NAME = "home"
MQTT_PASSWORD = "home123"
MQTT_TOPIC = "heating_raw/boiler_data"

week_day = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')

class mqtt_thread(Thread):
    def __init__(self, send_frame):
        Thread.__init__(self)
        self.stop = False
        self.send_frame = send_frame

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(MQTT_TOPIC)

    def on_message(self, client, userdata, msg):
        if not self.stop:
            data = msg.payload.decode('ascii')
            if data[0] != '1':
                return
            data = data[1:]
            dlen = len(data)
            if dlen % 8:
                return

            # print(dlen//8,end='')
            frame = frame_valid(decode_raw(data))
            if frame is not None:
                self.send_frame(frame)
                #print('{}'.format(frame))

    def run(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(MQTT_USER_NAME, password=MQTT_PASSWORD)
        client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 60)
        client.loop_start()
        while not self.stop:
            sleep(0.5)
        client.loop_stop()


class app_client():
    def __init__(self, root):
        self.root = root
        self.root.title("ST-480 data")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.style = Style()
        self.tab_font_head = ('Curier New', 10, 'bold')
        self.tab_font = ('Curier New', 10)
        self.style.configure('Red.TLabel', background='red', font=self.tab_font)
        self.style.configure('White.TLabel', background='white', font=self.tab_font)
        self.style.configure('Gray.TLabel', background='gray', font=self.tab_font_head)

        self.mainfrm = Frame(self.root, padding='7 0 7 7')
        self.mainfrm.pack(expand=1, fill=BOTH)

        self.frame_types = []
        self.frames = []
        self.values = []
        self.val_labels = []
        self.column_types = []

        self.cnt = 0
        self.empty = 0

        self.load_data()

        self.mqttThread = mqtt_thread(self.get_frame)
        self.mqttThread.start()

    def create_frame(self, keys, vals):
        self.cnt += 1
        frm = LabelFrame(self.mainfrm, text='Frame {}'.format(self.cnt), padding='3 3 3 3')
        values = []
        labels = []
        id_lab = Label(frm, text='id (hex)', style="Gray.TLabel", anchor=CENTER)
        id_lab.grid(row=0, column=0, sticky=W+E, padx=1, pady=3)
        Grid.columnconfigure(frm, 0, weight=1)
        val_lab = Label(frm, text='value', style="Gray.TLabel", anchor=CENTER)
        val_lab.grid(row=0, column=1, sticky=W+E, padx=1, pady=3)
        Grid.columnconfigure(frm, 1, weight=1)
        cnt = 1
        types = []
        for i in range(len(keys)):
            key = keys[i]
            var = vals[i]
            types.append(0)
            name_label = Label(frm, text='{0} ({0:04X})'.format(key))
            name_label.grid(row=cnt, column=0, padx=3, pady=1, sticky=W+E)
            values.append(var)
            val_label = Label(frm, text='{}'.format(var), style="Red.TLabel")
            val_label.grid(row=cnt, column=1, padx=3, pady=1, sticky=W+E)
            val_label.bind('<Button-1>', lambda e,x=self.cnt-1, y=cnt-1: self.change_type(x, y))
            labels.append(val_label)
            cnt += 1
        frm.pack(side=LEFT, expand=1, fill=Y, padx=10 if len(self.frame_types) & 1 else 0)
        self.frame_types.append(keys)
        self.frames.append(frm)
        self.values.append(values)
        self.val_labels.append(labels)
        self.column_types.append(types)

    def change_type(self, x, y):
        #print('Item {},{}'.format(x+1, y+1))# .. {}'.format(x+1, y+1, self.frames[x][y]))
        thistype = self.column_types[x][y]
        nexttype = (thistype + 1) % 10
        #print('Change type {} -> {}'.format(thistype, nexttype))
        self.column_types[x][y] = nexttype
        self.show_value(x, y)

    def show_value(self, x, y):
        try:
            val = self.values[x][y]
            typ = self.column_types[x][y]
            if typ == 1:  # degrees, 1 decimal
                strval = '{:0.1f}°C'.format(val/10)
            elif typ == 2:  # degrees
                strval = '{}°C'.format(val)
            elif typ == 3:  # percent
                strval = '{}%'.format(val)
            elif typ == 4:  # min / max
                valH = val >> 8
                valL = val & 0xFF
                strval = '{} / {}'.format(valL, valH)
            elif typ == 5:  # hours
                strval = '{}h'.format(val)
            elif typ == 6:  # clock
                valH = val >> 8
                valL = val & 0xFF
                strval = '{}:{:02}'.format(valH, valL)
            elif typ == 7:  # on / off
                strval = 'ON' if val else 'OFF'
            elif typ == 8:  # fuel % / kg
                valH = val >> 9
                valL = val & 0x1FF
                strval = '{}%, {}kg'.format(valH, valL)
            elif typ == 9:  # day of week
                strval = week_day[val % 7]
            else:
                strval = str(self.values[x][y])
                self.column_types[x][y] = 0
            self.val_labels[x][y].config(text='{}'.format(strval))
        except IndexError:
            pass

    def get_frame(self, frame):
        try:
        #if True:
            if frame == []:
                self.empty += 1
                self.empty %= 2
            elif self.empty == 1:
                keys, values = frame_keys(frame)
                if keys not in self.frame_types:
                    self.create_frame(keys, values)
                else:
                    for i in range(len(self.frame_types)):
                        if keys == self.frame_types[i]:
                            for j in range(len(values)):
                                if self.values[i][j] != values[j]:
                                    self.values[i][j] = values[j]
                                    self.show_value(i, j)
                                    #self.val_labels[i][j].config(text='{}'.format(values[j]))
                                    self.val_labels[i][j].config(style="Red.TLabel")
                                else:
                                    self.val_labels[i][j].config(style='White.TLabel')
        except:
            pass

    def load_data(self):
        top = parse('config.xml').getroot()
        frms = top.findall('frame')
        fcnt = 0
        for f in frms:
            #print(f.get('name'))
            itms = f.findall('item')
            keys = []
            values = []
            types = []
            icnt = 0
            for i in itms:
                #print(i.get('id'))
                keys.append(int(i.get('id').split('x')[1], 16))
                values.append(int(i.get('value')))
                types.append(int(i.get('type')))
            self.create_frame(keys, values)
            self.column_types[fcnt] = types
            for i in itms:
                self.show_value(fcnt, icnt)
                icnt += 1
            fcnt += 1
        pass

    def save_data(self):
        top = Element('ST-480')
        # table of types
        child = SubElement(top, 'types')
        SubElement(child, 'type', id='0', name='unknown')
        SubElement(child, 'type', id='1', name='temperature 1d')
        SubElement(child, 'type', id='2', name='temperature')
        SubElement(child, 'type', id='3', name='percent')
        SubElement(child, 'type', id='4', name='min / max')
        SubElement(child, 'type', id='5', name='hours')
        SubElement(child, 'type', id='6', name='clock')
        SubElement(child, 'type', id='7', name='on / off')
        SubElement(child, 'type', id='8', name='fuel % / kg')
        SubElement(child, 'type', id='9', name='day of week')
        # fames
        for x in range(len(self.frames)):
            child = SubElement(top, 'frame', name=self.frames[x]['text'])
            for y in range(len(self.frame_types[x])):
                subchild = SubElement(child, 'item', id='0x{:04X}'.format(self.frame_types[x][y]),
                                      value='{}'.format(self.values[x][y]), type='{}'.format(self.column_types[x][y]))
        f = open('config.xml', 'wb')
        f.write(tostring(top, pretty_print=True))
        f.close()

    def on_close(self):
        self.mqttThread.stop = True
        self.save_data()
        self.mqttThread.join(1.0)
        self.root.destroy()


if __name__ == "__main__":

    root = Tk()
    app = app_client(root)
    root.mainloop()


