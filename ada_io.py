# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
import ssl
import os
import microcontroller
import socketpool
import wifi
import board
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT




class Ada_IO:
    
    def __init__(self, *, on_connect = None, 
                          on_disconnect = None, 
                          on_message = None, 
                          on_publish = None,
                          on_subscribe = None,
                          on_unsubscribe = None):
        
        self._connect_to_wifi()
        
        # initialize Adafruit IO MQTT helper, not yet connected
        self.io = self._init_ada_io()
        
        self.io.on_connect = on_connect
        self.io.on_disconnect = on_disconnect
        self.io.on_message = on_message
        self.io.on_publish = on_publish
        self.io.on_subscribe = on_subscribe
        self.io.on_unsubscribe = on_unsubscribe
        


        
    def _connect_to_wifi(self) -> None:
        try:
            print(f'Connecting to network "{os.getenv("CIRCUITPY_WIFI_SSID")}": ', end='')
            wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
            print('CONNECTED')
            print(f'IP address: {wifi.radio.ipv4_address}')
        except Exception as ex:
            # TODO: could make this a loop that retries a few times before microcontroller reset
            print('\nFailed to connect. Error:', ex)
            print('Board will hard reset in 60 seconds.')
            time.sleep(60)
            microcontroller.reset()
            
            
    
    def _init_ada_io(self) -> IO_MQTT:
                               
        # create a socket pool
        pool = socketpool.SocketPool(wifi.radio)
        
        # initial a new MQTT client
        mqtt_client = MQTT.MQTT(
            broker='io.adafruit.com',
            username=os.getenv('ADAFRUIT_AIO_USERNAME'),
            password=os.getenv('ADAFRUIT_AIO_KEY'),
            socket_pool=pool,
            ssl_context=ssl.create_default_context()
            )
        
        io = IO_MQTT(mqtt_client)
        
        return io
        
    

    @property
    def is_connected(self) -> bool:
        return self.io.is_connected
        
       
       
    def connect(self) -> None:
        self.io.connect()
        
    
    def loop(self) -> None:
        self.io.loop()
        
        
    def publish(self, feed: str, value) -> None:
        self.io.publish(feed, value)
        
    
        