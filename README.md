# Bot Slartibartfast
Slartibartfast carries CO2, temp, humidity, ~~PM2.5~~ (not yet connected) sensors.  It holds a small display to show sensor values and recent sensor history.  It also uploads data to web dashboard.


![](https://github.com/teenyHermitCrab/Bot_Slartibartfast/blob/main/_misc/Slartibartfast_demo.gif)
<br/>
#### Ada IO web dashboard
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
<br/>
<br/>

I had been wondering about various scenarios regarding CO2 levels inside home.
- CO2 levels during cooking.  
- Is there a noticeable difference in overnight CO2 profile when sleeping in a closed room compared to ventilated room.
- How much does using a range hood mitigate CO2 levels when cooking?  Does the vent speed on our range hood actually make a significant difference?
- How much do 4-legged critters affect overnight levels?
- How much does a slightly open window improve levels compared to a fully open one.
- What is CO2 profile when I use van to car camp prior to early morning trail runs? Volume of this 'bedroom' is quite small.



#### display
A small color TFT (240x135) display provides access to sensor values.  
- *Top button* shows all sensor values.
- *Middle button* cycles through CO2, temperature, and humidity values.  The individual screens are easier to read on this small display.
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

- *Bottom button* cycles through 2-hour sensor history
<br/>


## Hardware
- [ESP32-S2 Reverse TFT Feather](https://www.adafruit.com/product/5345)
- [Adafruit SCD-41 - True CO2 Temperature and Humidity Sensor - STEMMA QT / Qwiic](https://www.adafruit.com/product/5190)

### misc
- [STEMMA QT / Qwiic JST SH 4-Pin Cable - 50mm Long](https://www.adafruit.com/product/4399)
<br/>

## Code Dependencies
- [Adafruit CircuitPython](https://github.com/adafruit/circuitpython)
- libraries .  TODO: list individually and point to a .zip
  <br/>


## Implementation notes
Sensor, web dashboard, and other objects have been moved into their own modules to minimize code in `code.py`.  


### How to install and run code on microprocessor board
#### How to install CircuitPython on microprocessor board
TODO: write up the CircuitPython boot loader install 
#### How to install dependencies on board
a simple copy to board **lib** folder.  Show example?

### How to setup PyCharm 
TODO: write up PyCharm setup
- disable auto-save if connecting to D:\
- installing dependencies: install to virtual env
- there was something else...
- 
#### serial port monitoring from PyCharm
While you can use a terminal program, it is not hard to connect to serial port inside PyCharm.  

Install `tio` to connect to serial devices via PyCharm terminal

`tio` is a serial device tool which features a straightforward command-line and configuration file interface to easily connect to serial TTY devices for basic I/O operations.  
This was how I installed on Windows 11

1. install `msys2`
    find installer at https://www.msys2.org/

2. after install `msys2`, install `tio`.  On commandline:
   ```
    C:Users\CorkHorde> pacman -S tio
   ```

4. after tio install, connect your serial device and use following command to list devices.  (You can also do this from PyCharm terminal)
    ```
    C:Users\CorkHorde> tio --list
        Device            TID     Uptime [s] Driver           Description
    ----------------- ---- ------------- ---------------- --------------------------
    /dev/ttyS5             568943867.930
    /dev/ttyS7             568943867.930
    
    C:Users\CorkHorde>
    ```

    In my case, my microprocessor board is ttyS7

5. On PyCharm terminal, connect to your serial device.  You should now see serial output from board.
   ```
     tio /dev/ttyS7
   ```




## References
- [ASHRAE position paper on CO2](https://www.ashrae.org/file%20library/about/position%20documents/pd_indoorcarbondioxide_2022.pdf)
- There are many charts online.  [Here is an overview](https://www.co2meter.com/blogs/news/carbon-dioxide-indoor-levels-chart) from a company selling CO2 sensors
<br/> 

## TODO:
- screen is loose on front of bot.  
- complete dependencies section on this readme.
- Add settings file.
- Upload to web dashboard should send average value of upload interval, similar to graph display mode..  Currently it is sending the most recent value.
- Experiment with putting dashboard, sensor, and maybe button monitoring on own task.  CircuitPython doesn't have `threading` module, but does have `asyncio`.
- Add PM2.5 sensor.  Ikea hack would be interesting: https://www.ikea.com/us/en/p/vindriktning-air-quality-sensor-60515911/
- Get larger standalone TFT display running with good layout.  Add settings file fields to allow easy swap.  This is probably a lot of fields since have to deal with sprite locations, font sizes, etc
- Add small WiFi and dashboard connections symbols. (maybe only do this on larger screens, 240x135 is too small)
- should create new fonts for single-value mode.  scaling up current fonts gets jaggy.
- get logging to work. do we need to add an SD card module or external switch? recall that file writes are default disabled.
  - There are occasional crashes not currently being addressed.  Probably can see them if using `tio` to view serial output.
- Dashboard is currently at Adafruit IO.  Try out other options: Azure, AWS, Heroku
- Need to check out edge cases for graphing plots.
  - might have to add autoscaling
  - values off outside **X** or **Y** scales leave artifacts on graph edge.
    - easy fix: clip values going into graph.
    - better: update `uplot` library
- clean up screen mounting on Slartibartfast - perhaps cutout a channel for bamboo mount plate.  Or give bot separate arms to grasp bamboo mount.
- ~~allow multiple wifi networks.~~
- ~~allow no wifi connection - recheck for network~~ (time this. if long check time, then only check at specified interval.  When you add asyncio, then it can check on its own)
- ~~Update demo .gif  - show new graph display.  Mount on bot~~
- ~~reduce bitmap file sizes.  Convert RGB files to indexed format~~
- ~~look through `lib` folder.  There might be dependencies that I'm no longer using~~
- ~~Add a third display mode that shows graph history of values.  How much memory is available on ESP32-S2?  Recall that writing to filesystem is default disabled.~~
- ~~Layout for single data mode: temp/humidity feels unbalanced.~~
- ~~Probably can save a little space: Converting top-level display to use same sprites as single display mode~~
- ~~Graphing plots should average for each minute to get a 2-hour plot (or could have that be part of graph-cycling?)~~

