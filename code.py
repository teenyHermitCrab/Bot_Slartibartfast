import asyncio
import os
import time
import traceback
# below are Adafruit imports
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label,  wrap_text_to_lines
from adafruit_io.adafruit_io import IO_MQTT, AdafruitIO_MQTTError
import adafruit_minimqtt.adafruit_minimqtt as MQTT
#import adafruit_scd4x
import board
import displayio
import microcontroller
import neopixel
import socketpool
import wifi
# below are local modules
from air_quality_sensors import AirSensor_SCD4x
from ada_io import Ada_IO
import callbacks


# on-board NeoPixel
pixel = neopixel.NeoPixel(pin=board.NEOPIXEL, n=1, brightness=0.25)
pixel.fill(0)

display = board.DISPLAY

# CO2, temp, humidity sensor
sensor = AirSensor_SCD4x()


# connection to Adafruit IO dashboard
# will have to check API to see if there is a way to determine avaliable feeds
# right now, this will not error if there is not a feed present at Adafruit IO
feeds = ['neopixel']
connected = callbacks.get_connected_callback(feeds)
message = callbacks.get_message_callback(pixel)
io = Ada_IO(on_connect = connected,
            on_message = message)




bitmap = displayio.OnDiskBitmap(r".\bitmaps\co2_temp_humidity.bmp")
tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
group = displayio.Group()
group.append(tile_grid)

font_file = r".\fonts\LeagueSpartan-Bold-16.bdf"
font = bitmap_font.load_font(font_file)

temp, humidity, co2 = 22, 33, 4444
co2_text = bitmap_label.Label(font, text='----', x=20, y=80, color=0xFFFFFF, scale=1)
#co2_units = bitmap_label.Label(font, text='ppm', x=30, y=100, color=0xFFFFFF, scale=1)
temp_text = bitmap_label.Label(font, text=f'--{chr(176)} F', x=100, y=80, color=0xFFFFFF, scale=1)
humidity_text = bitmap_label.Label(font, text='-- %', x=180, y=80, color=0xFFFFFF, scale=1)


group.append(co2_text)
#group.append(co2_units)
group.append(humidity_text)
group.append(temp_text)
display.root_group = group


timestamp = 0
while True:
    try:
        # keep connect in loop so that it reconnects if odd disconnection
        if not io.is_connected:
            print('Connecting to Adafruit IO:')
            # TODO: what is result if failed to connect
            #       does this throw exception
            io.connect()
            print('Connection to Adafruit done.')

        # pump message loop - allows us to respond to dashboard events.
        io.loop()


        if sensor.data_ready:
            co2 = sensor.CO2
            temp_c = sensor.temperature
            temp_f = (temp_c*9/5)+32
            humidity = sensor.relative_humidity

            co2_text.text = f'{co2: <4}'
            temp_text.text = f'{temp_f:0.0f}{chr(176)} F'
            humidity_text.text = f'{humidity:0.0f} %'

            print()
            print(f'        CO2 : {co2:>5} ppm' )
            print(f'Temperature : {temp_f:>5.1f} {chr(176)}F    ({temp_c:.1f} {"\u00b0"}C)' )
            print(f'   Humidity : {humidity:>5.1f} %' )
            # probably could publish all at once, it might just be using single publish under the hood
            if io.is_connected:
                io.publish('air-quality-sensors.co2', co2)
                io.publish('air-quality-sensors.humidity', humidity)
                io.publish('air-quality-sensors.temperature', temp_f)

    # exception case is mostly
    except OSError as ex:
        if 'ENOTCONN' in str(ex):     # [Errno 128] ENOTCONN
            print('#' * 40)
            print(ex)
            print(f'Adafruit connection error: restarting wifi and Adafruit connection')
            io = Ada_IO(on_connect = connected,
                        on_message = message)
            print(f'reconnect to AdaFruit IO successful')
            print('#' * 40)


    except Exception as e:  # pylint disable=broad-except
        # TODO: investigate Exception types recieved.  probaly could just try reinit Ada IO
        #       a few times before resetting microcontroller

        # TODO: log these exceptions locally when you get SD support added,
        print(f'Error: {e}')
        print(f'using traceback:\n{traceback.print_exception(e)}')
        # https://docs.circuitpython.org/en/latest/shared-bindings/wifi/index.html#wifi.Radio.connect
        # " Reconnections are handled automatically once one connection succeeds."


        # TODO: may not need a
        reset_delay = 35
        print(f'error: {e}\nresetting board in {reset_delay} seconds')

        count = 0
        for _ in range(reset_delay):
            time.sleep(1)
            count += 1
            if count >= 50:
                print()
                count = 0
            print('.', end='')
            count += 1

        print()
        microcontroller.reset()




