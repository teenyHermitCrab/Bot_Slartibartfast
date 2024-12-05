# SPDX-FileCopyrightText: 2020 by Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
#
# https://docs.circuitpython.org/projects/scd4x/en/stable/api.html#
import os
import time
# adafruit hardware imports below
import board
import adafruit_scd4x

#i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
scd4x = adafruit_scd4x.SCD4X(i2c)
print(f'serial number CO2 sensor: {''.join([str(i) for i in scd4x.serial_number])}')
print(f'WIFI name: {os.getenv("CIRCUITPY_WIFI_SSID")}')

print('starting measurements.')
#scd4x.start_periodic_measurement()
print('waiting for first measurement....\n')

#scd4x.set_ambient_pressure()


while False:
    if scd4x.data_ready:
        print(f'CO2        : {scd4x.CO2:<4} ppm' )
        temp_c = scd4x.temperature
        temp_f = (temp_c*9/5)+32
        print(f'Temperature: {temp_f:<4.1f} F   ({temp_c:<4.1f} C)' )
        print(f'Humidity   : {scd4x.relative_humidity:<4.1f} %' )
        print()
    #time.sleep(.01)
