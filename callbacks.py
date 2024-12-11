import adafruit_minimqtt.adafruit_minimqtt as MQTT
from neopixel import NeoPixel

"""
This file is just a spot to define callbacks, 
They could be in code.py and that would be easier for methods like message

But trying to keep code.py as clean as reasonably possible
"""

def get_connected_callback(feeds: list[str]):
    def connected(client: MQTT.MQTT):
        #feed: str = 'air-quality-sensors.neopixel'
        for feed in feeds:
            print(f'Adafruit IO feed subscription "{feed}": ', end = '')
            client.subscribe(feed)
            print('SUBSCRIBED.')
    return connected
    
    
# checkout regular library bundle and community bundle to see if typing module implemented
def get_message_callback(pixel: NeoPixel):
    # don't think this could be made general use.
    # We'll have to know beforehand what to we are going to do with these messages.
    
    def message(client: MQTT.MQTT, feed_id: str, payload):  # pylint: disable-unused-argument
        print(f'{feed_id=} received new value: {payload.upper()}')
        #feed_on_board_neopixel: str = 'air-quality-sensors.neopixel'
        feed_on_board_neopixel: str = 'neopixel'
        if feed_id == feed_on_board_neopixel:
            # colorpicker block appears to send '#------' format where - is a hex digit
            pixel.fill(int(payload[1:], 16))

        #  add other handlers here
    return message