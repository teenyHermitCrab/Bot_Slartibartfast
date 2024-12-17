import time
import traceback
# below are Adafruit imports
from adafruit_debouncer import Debouncer
import board
import digitalio
import microcontroller
import neopixel
# below are local modules
from air_quality_sensors import AirSensorSCD4x
from adafruitdashboard import AdaFruitDashboard
from bot_screen import BotScreen
import callbacks


# on-board NeoPixel
# 25% brightness is good enough for most indoor environments, would be too bright for night.
# full power not recommended since there is no heat sink on 5x5 board
pixel = neopixel.NeoPixel(pin=board.NEOPIXEL, n=1, brightness=0.25)
pixel.fill(0)

# on-board display 
# release any currently configured displays, 
#displayio.release_displays()
#You do not need to do this for boards with built-in displays, check if this would create errors

# CO2, temp, humidity sensor
sensor = AirSensorSCD4x(measurement_mode = AirSensorSCD4x.MeasurementMode.FAST )
# display screen mounted on ESP32-S2 Reverse TFT
bot_screen = BotScreen()

# connection to Adafruit IO dashboard
# will have to check API to see if there is a way to determine available feeds
# right now, this will not error if there is not a feed present at Adafruit IO
feeds = ['neopixel']
connected = callbacks.get_connected_callback(feeds)
message = callbacks.get_message_callback(pixel)
io = AdaFruitDashboard(on_connect = connected,
                       on_message = message)

# TODO: move button monitoring to its own object/task?
d0 = digitalio.DigitalInOut(board.D0)
d0.direction = digitalio.Direction.INPUT
d0.pull = digitalio.Pull.UP
button0 = Debouncer(d0)

d1 = digitalio.DigitalInOut(board.D1)
d1.direction = digitalio.Direction.INPUT
d1.pull = digitalio.Pull.DOWN
button1 = Debouncer(d1)

d2 = digitalio.DigitalInOut(board.D2)
d2.direction = digitalio.Direction.INPUT
d2.pull = digitalio.Pull.DOWN
button2 = Debouncer(d2)



timestamp = 0
dashboard_interval = 60  #Adafruit IO dashboard upload interval in seconds
while True:
    try:
        # keep connect in loop so that it reconnects if odd disconnection
        if not io.is_connected:
            print('Connecting to Adafruit IO:')
            io.connect()
            print('Connection to Adafruit done.')

        # pump message loop - allows us to respond to dashboard events.
        # this call is up to a few seconds.  Disabled for now
        # make sensors, display, and dashboard use their own threads
        #io.loop()

        button0.update()
        button1.update()
        button2.update()
        if button0.rose:
            bot_screen.show_top_display()
        if button1.rose:
            bot_screen.show_single_value_display()
        if button2.rose:
            bot_screen.show_single_graph_display()


        if sensor.data_ready:
            co2 = sensor.CO2
            temp_c = sensor.temperature
            temp_f = (temp_c*9/5)+32
            humidity = sensor.relative_humidity
            
            bot_screen.update_values(co2 = co2, temperature_c = temp_c, humidity = humidity)

            print()
            print(f'        CO2 : {co2:>5} ppm' )
            print(f'Temperature : {temp_f:>5.1f} {chr(176)}F    ({temp_c:.1f} {"\u00b0"}C)' )
            print(f'   Humidity : {humidity:>5.1f}%' )
            # probably could publish all at once, it might just be using single publish under the hood
            
            # publish to AdaFruit only at a certain interval, 
            if (time.monotonic() - timestamp) >= dashboard_interval:
                timestamp = time.monotonic()
                if io.is_connected:
                    print(f'\nuploading to dashboard: ')
                    io.publish('air-quality-sensors.co2', co2)
                    io.publish('air-quality-sensors.humidity', humidity)
                    io.publish('air-quality-sensors.temperature', temp_f)

    # exception case seems to originate from .publish but will need on-board logging to catch this.
    # Recall that file-writes are default disabled
    except OSError as ex:
        if 'ENOTCONN' in str(ex):     # [Errno 128] ENOTCONN
            print('#' * 40)
            print(ex)
            print(f'Adafruit connection error: restarting wifi and Adafruit connection')
            io = AdaFruitDashboard(on_connect = connected,
                                   on_message = message)
            print(f'reconnect to AdaFruit IO successful')
            print('#' * 40)


    except Exception as e:  # pylint disable=broad-except
        # TODO: investigate Exception types received.  probably could just try reinit Ada IO
        #       a few times before resetting microcontroller

        # TODO: log these exceptions locally when you get SD support added,
        print(f'Error: {e}')
        print(f'using traceback:\n{traceback.print_exception(e)}')
        # https://docs.circuitpython.org/en/latest/shared-bindings/wifi/index.html#wifi.Radio.connect
        # " Reconnections are handled automatically once one connection succeeds."


        # TODO: may not need a
        reset_delay = 60
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




