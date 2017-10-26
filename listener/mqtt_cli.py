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
            sleep(0.2)
        client.loop_stop()


class app_client():
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.mainfrm = Frame(self.root)
        self.mainfrm.pack(expand=1, fill=BOTH)

        self.mqttThread = mqtt_thread(self.get_frame)
        self.mqttThread.start()

        self.frame_types = []
        self.frames = []
        self.values = []
        self.val_labels = []

        self.cnt = 0
        self.empty = 0

    def create_frame(self, keys, vals):
        self.cnt += 1
        frm = LabelFrame(self.mainfrm, text='Frame {}'.format(self.cnt))
        values = []
        labels = []
        id_lab = Label(frm, text='id')
        id_lab.grid(row=0, column=0)
        val_lab = Label(frm, text='value')
        val_lab.grid(row=0, column=1)
        cnt = 1
        for i in range(len(keys)):
            key = keys[i]
            var = vals[i]
            name_label = Label(frm, text='{0} ({0:04X}h)'.format(key))
            name_label.grid(row=cnt, column=0, padx=3, sticky=E)
            values.append(var)
            val_label = Label(frm, text='{}'.format(var))
            val_label.grid(row=cnt, column=1, padx=3, sticky=W+E)
            Grid.columnconfigure(frm, 1, weight=1)
            labels.append(val_label)
            cnt += 1
        frm.pack(side=LEFT, expand=1, fill=Y)
        self.frame_types.append(keys)
        self.frames.append(frm)
        self.values.append(values)
        self.val_labels.append(labels)

    def get_frame(self, frame):
        if frame == []:
            self.empty += 1
            self.empty %= 8
            return
        if self.empty != 1:
            return
        keys, values = frame_keys(frame)
        if keys not in self.frame_types:
            self.create_frame(keys, values)
            return
        for i in range(len(self.frame_types)):
            if keys == self.frame_types[i]:
                for j in range(len(values)):
                    if self.values[i][j] != values[j]:
                        self.values[i][j] = values[j]
                        self.val_labels[i][j].config(text='{}'.format(values[j]))
                        self.val_labels[i][j].config(style="Red.TLabel")
                    else:
                        self.val_labels[i][j].config(style='White.TLabel')
                return

    def on_close(self):
        self.mqttThread.stop = True
        self.mqttThread.join()
        print(self.frame_types)
        self.root.destroy()


if __name__ == "__main__":

    root = Tk()
    style = Style()
    style.configure("Red.TLabel", background='red')
    style.configure("White.TLabel", background='white')
    app = app_client(root)
    root.mainloop()


