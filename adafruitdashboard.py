import time
import traceback
import ssl
import os
import microcontroller
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT


class AdaFruitDashboard:
    
    def __init__(self, *, on_connect = None, 
                          on_disconnect = None, 
                          on_message = None, 
                          on_publish = None,
                          on_subscribe = None,
                          on_unsubscribe = None):
        """

        """
        
        #self._connect_to_wifi()
        self._connect_to_available_wifi()



        # TODO: probably should split up wifi and Adafruit wrappers

        # initialize Adafruit IO MQTT helper, not yet connected
        self.io = None
        if self.connected_to_wifi:
            self.io = self._init_ada_io()

            self.io.on_connect = on_connect
            self.io.on_disconnect = on_disconnect
            self.io.on_message = on_message
            self.io.on_publish = on_publish
            self.io.on_subscribe = on_subscribe
            self.io.on_unsubscribe = on_unsubscribe


    @property
    def connected_to_wifi(self):
        return wifi.radio.connected


    # @staticmethod
    # def _connect_to_wifi() -> None:
    #     """Expects to find Wi-Fi credentials in settings.toml
    #     """
    #     try:
    #         print(f'Connecting to network "{os.getenv("CIRCUITPY_WIFI_SSID")}": ', end='')
    #         wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
    #         print('CONNECTED')
    #         print(f'IP address: {wifi.radio.ipv4_address}')
    #     except Exception as ex:
    #         # TODO: could make this a loop that retries a few times before microcontroller reset
    #         # TODO: when you figure out how to write to local log (default: writes are disabled) make sure to log this
    #         print('\nFailed to connect. Error:', ex)
    #         print('Board will hard reset in 60 seconds.')
    #         time.sleep(60)
    #         microcontroller.reset()


    @staticmethod
    def _connect_to_available_wifi() -> bool:
        # NOTE: using 'eval' for now:
        #   1. there is no user input here
        #   2. no configparser or similar in CircuitPython, and os.getenv is only strings and ints(floats?).
        #   3. os.getenv also does not support sections
        #   4. could have a separate .py file as settings and just import that.  but then would also need to make sure
        #      this is specifically excluded in .gitignore
        target_networks: dict = eval(os.getenv('NETWORKS'))
        target_ssids = target_networks.keys()

        try:
            print('start wifi scan..')
            timestamp=time.monotonic()
            wifi.radio.stop_scanning_networks()
            # TODO: further tests required here.  can I connect while still in scanning mode?
            #       Could allow to test multiple available networks
            for network in wifi.radio.start_scanning_networks():
                if network.ssid in target_ssids:
                    print(f'found {network.ssid=}')
                    wifi.radio.stop_scanning_networks()
                    pwd = target_networks[network.ssid]
                    wifi.radio.connect(network.ssid, pwd)
                    print(f'connected to {network.ssid=}')
                    break
            duration = time.monotonic() - timestamp
            print(f'stop wifi scan {duration=}')
            return wifi.radio.connected
        # TODO: could make this a loop that retries a few times before microcontroller reset
        # TODO: when you figure out how to write to local log (default: writes are disabled) make sure to log this
        except Exception as e:
            print(f'Error: {e}')
            print(f'using traceback:\n{traceback.print_exception(e)}')
            return False
            # print('\nFailed to connect. Error:', ex)
            # print('Board will hard reset in 60 seconds.')
            # time.sleep(60)
            # microcontroller.reset()







    
    def _init_ada_io(self) -> IO_MQTT:
        """Expects to find Adafruit IO credentials in settings.toml"""

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
    def is_connected_to_dashboard(self) -> bool:
        return self.io is not None and self.io.is_connected
       
       
    def connect_to_dashboard(self) -> None:
        self.io.connect()
        
    
    def loop(self) -> None:
        """Manually process messages from Adafruit IO.

        Call this method to check incoming subscription messages.
        """
        self.io.loop()
        
        
    def publish(self, feed: str, value) -> None:
        """Publishes to an Adafruit IO Feed.

        :param feed: – Adafruit IO Feed key.
        :param value: – Data to publish to the feed or group.
        """

        # TODO: test metadata, is_group parameters
        self.io.publish(feed, value)
