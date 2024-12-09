# Bot_Slartibartfast
CO2, temp, humidity, 2.5 sensor.  Uploads to dashboard.

## Dependencies
- [Adafruit CircuitPython](https://github.com/adafruit/circuitpython)
- libraries .  list individually and point to a .zip

## Description
Bot Slartibartfast hosts air quality sensors. It has a small TFT display for displaying values. Buttons next to display cycle the display modes. It also uploads data to Adafruit IO.

#### display
A small color TFT (240x135) display provides access to sensor values.  
- There is a top-level screen to show all values.
- You can also individually cycle through CO2, temperature, and humidity values.  The individual screens are easier to read on this small display.
  - For CO2 display, there is also an emoji to interpret the PPM units display.

|    PPM range  | interpretation| emoji  |
|--------------:|:-----------|:----------:|
|     0 - 0449  | great      |            |
|   450 - 0749  | good       | []()       |
|   750 - 1249  | OK         | []()       |
|  1250 - 1249  | concerning | []()       |
|  1250 - 1999  | ventilate  | []()       |
|  2000 - 4999  | unhealthy  | []()       |
|  5000 - 9999  | harmful    | []()       |
|  10K and up   | danger     | []()       |

add a gif here to show operation


## Hardware
- [ESP32-S2 Reverse TFT Feather](https://www.adafruit.com/product/5345)
- [Adafruit SCD-41 - True CO2 Temperature and Humidity Sensor - STEMMA QT / Qwiic](https://www.adafruit.com/product/5190)

### misc
- [STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long](https://www.adafruit.com/product/4399)

## Implementation notes
Sensor, web dashboard, and other objects have been moved into their own modules to minimize code in `code.py`  


## TODO:
- reduce bitmap file sizes.  Convert RGB files to indexed format
- look through `lib` folder.  There might be dependencies that I'm no longer using
- Experiment with putting dashboard, sensor, and maybe button monitoring on own task.  CircuitPython doesn't have `threading` module, but does have `asyncio`.
- Add PM2.5 sensor.  Ikea hack would be interesting: https://www.ikea.com/us/en/p/vindriktning-air-quality-sensor-60515911/
- Add a third display mode that shows graph history of values.  How much memory is available on ESP32-S2?  Recall that writing to filesystem is default disabled.
- 
