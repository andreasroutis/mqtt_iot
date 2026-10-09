import paho.mqtt.client as mqtt
import ssl
import os
import sys

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from threading import Timer
from datetime import datetime


class IoTExample:
    def __init__(self):
        self.ax = None
        self._establish_mqtt_connection()
        self._prepare_graph_window()


# call this method to start the client loop
    def start(self):
        if self.ax:
            self.client.loop_start()
            plt.show()
        else:
            self.client.loop_forever()


# call this method to disconnect from the broker
    def disconnect(self, args=None):
        self.client.disconnect() # disconnect

# You need to fill this in, here we will place the commands
# For connecting to the broker

    def _establish_mqtt_connection(self):
        self.client = mqtt.Client()
        self.client.tls_set_context(ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
        self.client.on_log = self._on_log
        self.client.username_pw_set('iotlesson', 'YGK0tx5pbtkK2WkCBvJlJWCg')
        self.client.on_message = self._on_message
        self.client.connect('phoenix.medialab.ntua.gr', 8883)
        self.client.subscribe('hscnl/hscnl02/state/ZWaveNode005_Switch/state')
        self.client.subscribe('hscnl/hscnl02/state/ZWaveNode005_ElectricMeterWatts/state')
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode005_Switch', 'ON')

        



# This is the callback that will be called whenever a new message
# is received
    
    def _on_message(self, client, userdata, msg):
        if msg.topic == 'hscnl/hscnl02/state/ZWaveNode005_ElectricMeterWatts/state':
            self._add_value_to_plot(float(msg.payload.decode('utf-8')))
        print(msg.topic+' '+str(msg.payload.decode('utf-8')))


# This is the callback that will be called whenever a new log
# event is created
        
    def _on_log(self, client, userdata, level, buf):
        print('log: ', buf)

    def _prepare_graph_window(self):
# Plot variables
        plt.rcParams['toolbar'] = 'None'        
        axcut = plt.axes([0.0, 0.0, 0.1, 0.06])
        self.bcut = Button(axcut, 'ON')
        axcut2 = plt.axes([0.1, 0.0, 0.1, 0.06])
        self.bcut2 = Button(axcut2, 'OFF')
        self.state_field = plt.text(1.5, 0.3, 'STATE: -')
        self.bcut.on_clicked(self._button_on_clicked)
        self.bcut2.on_clicked(self._button_off_clicked)
        self.ax = plt.subplot(111)
        self.dataX = []
        self.dataY = []
        self.first_ts = datetime.now()
        self.lineplot, = self.ax.plot(
            self.dataX, self.dataY, linestyle='--', marker='o', color='b')
        self.ax.figure.canvas.mpl_connect('close_event', self.disconnect)
        self.finishing = False
        self._my_timer()

    def _refresh_plot(self):
        if len(self.dataX) > 0:
            self.ax.set_xlim(min(self.first_ts, min(self.dataX)),
                             max(max(self.dataX), datetime.now()))
            self.ax.set_ylim(min(self.dataY) * 0.8, max(self.dataY) * 1.2)
            self.ax.relim()
        else:
            self.ax.set_xlim(self.first_ts, datetime.now())
            self.ax.relim()
        plt.draw()

    def _add_value_to_plot(self, value):
        self.dataX.append(datetime.now())
        self.dataY.append(value)
        self.lineplot.set_data(self.dataX, self.dataY)
        self._refresh_plot()

    def _my_timer(self):
        self._refresh_plot()
        if not self.finishing:
            Timer(1.0, self._my_timer).start()

    def _button_on_clicked(self, event):
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode005_Switch', 'ON')

    def _button_off_clicked(self, event):
        self.client.publish('hscnl/hscnl02/sendcommand/ZWaveNode005_Switch', 'OFF')


try:
    iot_example = IoTExample()
    iot_example.start()
    
except KeyboardInterrupt:
    print('Interrupted')
    try:
        iot_example.disconnect()
        sys.exit(0)
    except SystemExit:
        os._exit(0)