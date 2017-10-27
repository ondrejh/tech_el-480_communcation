#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *

from threading import Thread

from time import sleep

import paho.mqtt.client as mqtt
from decode import decode_raw, frame_valid, frame_keys

MQTT_SERVER_IP = "192.168.1.200"
MQTT_SERVER_PORT = 1883
MQTT_USER_NAME = "home"
MQTT_PASSWORD = "home123"
MQTT_TOPIC = "heating_raw/boiler_data"


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

        self.cnt = 0
        self.empty = 0

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
        for i in range(len(keys)):
            key = keys[i]
            var = vals[i]
            name_label = Label(frm, text='{0} ({0:04X})'.format(key))
            name_label.grid(row=cnt, column=0, padx=3, pady=1, sticky=W+E)
            values.append(var)
            val_label = Label(frm, text='{}'.format(var), style="Red.TLabel")
            val_label.grid(row=cnt, column=1, padx=3, pady=1, sticky=W+E)
            labels.append(val_label)
            cnt += 1
        frm.pack(side=LEFT, expand=1, fill=Y, padx=10 if len(self.frame_types) & 1 else 0)
        self.frame_types.append(keys)
        self.frames.append(frm)
        self.values.append(values)
        self.val_labels.append(labels)

    def get_frame(self, frame):
        try:
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
                                    self.val_labels[i][j].config(text='{}'.format(values[j]))
                                    self.val_labels[i][j].config(style="Red.TLabel")
                                else:
                                    self.val_labels[i][j].config(style='White.TLabel')
        except:
            pass

    def on_close(self):
        self.mqttThread.stop = True
        self.mqttThread.join(1.0)
        self.root.destroy()


if __name__ == "__main__":

    root = Tk()
    app = app_client(root)
    root.mainloop()


