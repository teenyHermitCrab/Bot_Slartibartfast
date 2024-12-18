# Bot_Slartibartfast
CO2, temp, humidity, ~~PM2.5~~ (not yet connected) sensor.  Uploads to dashboard.



## Dependencies
- [Adafruit CircuitPython](https://github.com/adafruit/circuitpython)
- libraries .  list individually and point to a .zip

## Description
Bot Slartibartfast hosts air quality sensors. It has a small TFT display for displaying values. Buttons next to display cycle the display modes. 
Bot Slartibartfast also uploads data to Adafruit IO dashboard.

#### display
A small color TFT (240x135) display provides access to sensor values.  
- There is a top-level screen to show all values.
- You can also individually cycle through CO2, temperature, and humidity values.  The individual screens are easier to read on this small display.
  - For CO2 display, there is also an emoji to interpret the PPM units display.  Below is an example, probably will make this configurable
    <br/>

    |     PPM range | interpretation |                                                       emoji                                                       |
    |--------------:|:---------------|:-----------------------------------------------------------------------------------------------------------------:|
    |      0 - 0449 | great          |       ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/great.png)       |
    |    450 - 0749 | good           |       ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/good.png)        |
    |    750 - 1249 | OK             |      ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/neutral.png)      |
    |   1250 - 1249 | concerning     | ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/neutral_eyes_only.png) |
    |   1250 - 1999 | ventilate      |       ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/frown.png)       |
    |   2000 - 4999 | unhealthy      |  ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/frown_sweating.png)   |
    |   5000 - 9999 | harmful        | ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/fearful_openMouth.png) |
    |    10K and up | danger         |      ![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/individual_faces/danger.png)       |

    

#### operation demo
![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/co2_demo.gif)


#### Ada IO dashboard
<img width="736" alt="image" src="https://github.com/user-attachments/assets/89d5cb2f-6a46-4f91-bd6e-825a5bd85e02">


Currently, this data is being uploaded to Adafruit IO dashboard.  Will check out other options later.


Note:
- sensor is not located in fixed spot - data will be quite variable.
- This dashboard doesn't render perfectly on mobile, so there is a separate dashboard I use for mobile
- The dashboard only updates if you are logged into your Adafruit account, otherwise you'd have to manually refresh page.  I'm not concerned with this, since I plan to check out other dashboard options later.

###### Data with history:
https://io.adafruit.com/corkhorde/dashboards/air-quality-full

###### Current readings only
https://io.adafruit.com/corkhorde/dashboards/air-quality-mobile




## Hardware
- [ESP32-S2 Reverse TFT Feather](https://www.adafruit.com/product/5345)
- [Adafruit SCD-41 - True CO2 Temperature and Humidity Sensor - STEMMA QT / Qwiic](https://www.adafruit.com/product/5190)

### misc
- [STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long](https://www.adafruit.com/product/4399)

## Implementation notes
Sensor, web dashboard, and other objects have been moved into their own modules to minimize code in `code.py`  


## References
- [ASHRAE position paper on CO2](https://www.ashrae.org/file%20library/about/position%20documents/pd_indoorcarbondioxide_2022.pdf)
- There are many charts online.  [Here is an overview](https://www.co2meter.com/blogs/news/carbon-dioxide-indoor-levels-chart) from a company selling CO2 sensors
- 

## TODO:
- ~~reduce bitmap file sizes.  Convert RGB files to indexed format~~
- ~~look through `lib` folder.  There might be dependencies that I'm no longer using~~
- Experiment with putting dashboard, sensor, and maybe button monitoring on own task.  CircuitPython doesn't have `threading` module, but does have `asyncio`.
- Add PM2.5 sensor.  Ikea hack would be interesting: https://www.ikea.com/us/en/p/vindriktning-air-quality-sensor-60515911/
- ~~Add a third display mode that shows graph history of values.  How much memory is available on ESP32-S2?  Recall that writing to filesystem is default disabled.~~
- Get larger standalone TFT display running with good layout.  Add settings file fields to allow easy swap.  This is probably a lot of fields since have to deal with sprite locations, font sizes, etc
- Add small Wifi and dashboard connections symbols.
- ~~Layout for single data mode: temp/humidity feels unbalanced.~~
- should create new fonts for single-value mode.  scaling up current fonts looks terrible.
- ~~Probably can save a little space: Converting top-level display to use same sprites as single display mode~~
- Dashboard is currently at Adafruit IO.  Try out other options: Azure, AWS, Heroku
- Need to check out edge cases for graphing plots.  might have to add autoscaling
- Graphing plots should average for each minute to get a 2-hour plot (or could have that be part of graph-cycling?)
- Add settings file
