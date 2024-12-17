from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label
import adafruit_imageload
from adafruit_itertools import cycle
import board
from circuitpython_uplot.plot import Plot, color
from circuitpython_uplot.logging import Logging as Ulogging
import displayio
# local imports below
from enum import Enum  # no builtin Enum in CircuitPython, so this is a hack
   

class BotScreen:
    """There is not a huge amount of flash space on this board (after CircuitPython is loaded).
    So this first iteration is using sprites to share bitmap space across the main display modes.
    A bit more complicated to modify a display when switching sensors,
    
    Otherwise, we would have more TileGroups vs sprites, but that might be easier for code maintenance if adding a bunch of 
    extra display modes.

    Suppose there are various ways to do this, but for now I'm choosing to have one
    displayio.Group for each display mode. (top-level, single-data, single-graph).
    So when switching between sensors while in single-data or single-graph, we have to swap the
    fields with that display.

    Maybe it might be more straightforward to just have entirely separate display groups.
    Soo.. just added graphs and it looks like it might be easier to use separate display groups for each sensor
    
    TODO: add usage notes
    """

    # NOTE: using enum hack is kinda shiny, but then have to specify full name. E.g.:,  BotScreen._DisplayLevel.TOP.
    #       so kinda wordy.  Could just use an internal class here.  At least using Enum makes it
    #       clear what we are doing
    
    _DisplayLevel = Enum(TOP           = 0,  # all data fields
                         SINGLE_DATA   = 1,
                         SINGLE_GRAPH  = 2, )

    _Sensor = Enum(CO2         = 0,
                   TEMPERATURE = 1,
                   HUMIDITY    = 2, )

    # using emoji to interpret CO2 values on single mode display
    _BlobSprite = Enum(VERY_GOOD      = 0,
                       GOOD           = 1,
                       OK             = 2,
                       CONCERNING     = 3,
                       UNHEALTHY      = 4,
                       VERY_UNHEALTHY = 5,
                       DANGER         = 6, )
    
    
    # Index of group appends when constructing the top-level display.
    # Enum values are the displayio append index that we use to reach in and change appropriate text
    _FieldOrderTop = Enum(CO2         = 1,
                          TEMPERATURE = 3,
                          HUMIDITY    = 4, )

    # Index of group appends for single data mode screen
    _FieldOrderSingleData = Enum(SPRITE_SENSOR = 0,
                                 SPRITE_BLOB   = 1,
                                 DATA          = 2,
                                 UNITS         = 3, )
                                 
    #_FieldOrderSingleGraph = Enum(....)


    class GraphSingleSensor:
        """Class to wrap related objects and data for distinct displays.

        Contains:
        - display group. This is what gets assigned to root_group (which shows it on screen)
        - uplot logging object.  This is what updates new data to plot.  It is not a debug logger
        - x, y previous data.  The plot doesn't save previous x,y data.  It is just a drawing.
          We need the previous data when adding new points.
        """
        def __init__(self, group: displayio.Group, ulog: Ulogging ):
            self.display_group = group
            self.uplot_logging = ulog
            # uplot logging doesn't actually save the x,y points, it just draws on the plot
            # so save previous points, since we need to update this list when new data arrives
            self.x: list[int] = []
            self.y: list[int|float] = []
    
    _single_data_display_states  = cycle([_Sensor.CO2, _Sensor.TEMPERATURE, _Sensor.HUMIDITY])
    _single_graph_display_states = cycle([_Sensor.CO2, _Sensor.TEMPERATURE, _Sensor.HUMIDITY])

    
    def __init__(self, settings = None):
        """First iteration: don't worry about making this too general.  Just use as
           a spot to keep code out of code.py or robot level
        """
        
        # NOTE: not sure where these values will ultimate live.
        #       we cant just change these values to see an effect on display text.
        #
        #       setter for Label.text calls private method to make display change
        self._co2: int = None
        self._temperature_c: float = None
        self._temperature_f: float = None
        self._humidity: float = None

        # They are assigned to display.root_group to show on screen
        self._group_top: displayio.Group = self._init_group_top(settings)
        self._group_single_data: displayio.Group = self._init_group_single_data(settings)

        # going to use separate display groups from each sensor for graphs
        # we'll see if this is easier to maintain.
        # Each element of this list contains display group and uplot.logging object
        # assign group to root_group as usual.  Use the uplot logging object to add values to that plot.
        self._graph_displays: list[BotScreen.GraphSingleSensor] = [self._init_co2_graph(settings),
                                                                   self._init_temp_graph(settings),
                                                                   self._init_humidity_graph(settings), ]
        
        self._current_display_level = BotScreen._DisplayLevel.TOP
        # not the actual display, just which sensor is current
        self._current_single_data_sensor = next(BotScreen._single_data_display_states)
        self._current_single_graph_sensor = next(BotScreen._single_graph_display_states)

        self._display = board.DISPLAY
        self._display.root_group = self._group_top


    #region initialize top-level and single-sensor-value displays
    def _init_group_top(self, settings) -> displayio.Group:
        """Initial the top-level display."""
        # TODO: decide whether these go to a settings file.  That would probably make it easier to use different displays
        #       If so, may want to store percentage in settings file? then could have a helper method (knowing display resolution)
        #       that could translate to x,y values
        font_file = r".\fonts\Arial-Bold-24.bdf"
        font_top_values = bitmap_font.load_font(font_file)
        
        font_file = r'.\fonts\LeagueSpartan-Bold-16.bdf'
        font_top_units = bitmap_font.load_font(font_file)

        co2_label = bitmap_label.Label(font_top_values, text='----', 
                                       color=0xFFFFFF, scale=1,
                                       anchor_point = (1.0, 0.0), anchored_position = (80, 55))
        co2_units_label = bitmap_label.Label(font_top_units, text='ppm', 
                                             color=0xFFFFFF, scale=1,
                                             anchor_point = (1.0, 0.0), anchored_position = (80, 90))
        temperature_label = bitmap_label.Label(font_top_values, text=f'---{chr(176)}', 
                                               color=0xFFFFFF, scale=1, 
                                               anchor_point = (1.0, 0.0), anchored_position = (155, 55))
        humidity_label = bitmap_label.Label(font_top_values, text='--%', 
                                            color=0xFFFFFF, scale=1,
                                            anchor_point = (1.0, 0.0), anchored_position = (235, 55))
        
        bitmap_top = displayio.OnDiskBitmap(r".\bitmaps\co2_temp_humidity.bmp")
        tile_grid_top = displayio.TileGrid(bitmap_top, pixel_shader=bitmap_top.pixel_shader)
        
        group_top = displayio.Group()
        
        # Append order matters since the first element 'tile_grid_top' is a background, so it needs to be first
        # other elements (Label objects) could be in any order since they don't overlap, but keep this order so we can
        # reference the text values by append order. I.e., append in order of _TextOrderTopLevel
        group_top.append(tile_grid_top)
        group_top.append(co2_label) 
        group_top.append(co2_units_label)
        group_top.append(temperature_label)
        group_top.append(humidity_label)
        
        return group_top
        
        
    def _init_group_single_data(self, settings) -> displayio.Group:
        """Initialize display for single-data mode."""

        # TODO: decide whether these go to a settings file.  That would probably make it easier to use different displays
        #       If so, may want to store percentage in settings file? then could have a helper method (knowing display resolution)
        #       that could translate to x,y values
        
        font_file = r".\fonts\Arial-Bold-36.bdf"
        font_value = bitmap_font.load_font(font_file)
            
        font_file = r".\fonts\LeagueSpartan-Bold-16.bdf"
        font_units = bitmap_font.load_font(font_file)
        
        data_label = bitmap_label.Label(font_value, text='8888', 
                                              color=0xFFFFFF, scale=1,
                                              anchor_point = (1.0, 0.0), anchored_position = (90, 80))
        unit_label = bitmap_label.Label(font_units, text='ppm', 
                                        color=0xFFFFFF, scale=1,
                                        anchor_point = (0.0, 0.0), anchored_position = (100, 80))
         
        # we don't need an explicit black background, since display is already black when pixels are off
        #bitmap_black_background = displayio.OnDiskBitmap(r".\bitmaps\black_background.bmp")
        #tile_grid_background = displayio.TileGrid(bitmap_black_background, 
        #                                          pixel_shader=bitmap_black_background.pixel_shader)
                                                    
        # Load the sprite sheet for sensor symbols
        sprite_sheet1, palette1 = adafruit_imageload.load(r".\bitmaps\sensor_symbols_sprite_210x70.bmp",
                                                        bitmap=displayio.Bitmap,
                                                        palette=displayio.Palette)
        # Create a sprite for sensor symbols
        sprite_sensor = displayio.TileGrid(sprite_sheet1, pixel_shader=palette1,
                                           width = 1, height = 1,
                                           x = 160, y=5,
                                           tile_width = 70, tile_height = 70)
                                              
        sprite_sheet2, palette2 = adafruit_imageload.load(r".\bitmaps\blobs_black_background_680x80.bmp",
                                                        bitmap=displayio.Bitmap,
                                                        palette=displayio.Palette)
        # Create a sprite for emojis
        sprite_blob = displayio.TileGrid(sprite_sheet2, pixel_shader=palette2,
                                           width = 1, height = 1,
                                           x = 5, y=5,
                                           tile_width = 85, tile_height = 80)

        group_single_display = displayio.Group(scale = 1)
        # Append order matters since the first element 'tile_grid_top' is a background, so it needs to be first
        # other elements (Label objects) could be in any order since they dont overlap, but keep this order so we can 
        # reference the text values by append order. I.e., append in order of _TextOrderTopDisplay
        group_single_display.append(sprite_sensor)
        group_single_display.append(sprite_blob)
        group_single_display.append(data_label)
        group_single_display.append(unit_label)
        
        return group_single_display
    #endregion

    #region initialize graph displays
    def _init_co2_graph(self, settings) -> GraphSingleSensor:
        """Initialize CO2 graph

        Creates display group, uplot logging, x/y data storage
        """
        # TODO: add settings
        plot = self._generate_graph_base_plot(title = 'CO2')

        g = displayio.Group()
        g.append(plot)

        my_loggraph = Ulogging(plot=plot,
                               x=[], y=[],
                               rangex=[121, 0], rangey=[0, 2500],
                               line_color=color.BLUE,
                               ticksx=[120, 100, 80, 60, 40, 20, 1, ],
                               ticksy=[300, 650, 1000, 1750, 2500],
                               tick_pos=False,
                               #limits=[1000, 1750, ],
                               fill=True )

        return BotScreen.GraphSingleSensor(group = g, ulog = my_loggraph)

    def _init_temp_graph(self, settings) -> GraphSingleSensor:
        """Initialize temperature graph

        Creates display group, uplot logging, x/y data storage
        """
        # TODO: add settings
        plot = self._generate_graph_base_plot(title='°F')

        g = displayio.Group()
        g.append(plot)

        my_loggraph = Ulogging(plot=plot,
                               x=[], y=[],
                               rangex=[121, 0], rangey=[30, 110],
                               line_color=color.BLUE,
                               ticksx=[120, 100, 80, 60, 40, 20, 1, ],
                               ticksy=[ 50, 70, 80, 90, 110],
                               tick_pos=False,
                               #limits=[60, 100, ],
                               fill=True)

        return BotScreen.GraphSingleSensor(group=g, ulog=my_loggraph)

    def _init_humidity_graph(self, settings) -> GraphSingleSensor:
        """Initialize humidity graph

        Creates display group, uplot logging, x/y data storage
        """
        # TODO: add settings
        plot = self._generate_graph_base_plot(title='rH %')

        g = displayio.Group()
        g.append(plot)

        my_loggraph = Ulogging(plot=plot,
                               x=[], y=[],
                               rangex=[121, 0], rangey=[0, 100],
                               line_color=color.BLUE,
                               ticksx=[120, 100, 80, 60, 40, 20, 1, ],
                               ticksy=[ 20, 40, 60, 80, 100],
                               tick_pos=False,
                               #
                               limits=[20, 65,],
                               fill=True)

        return BotScreen.GraphSingleSensor(group=g, ulog=my_loggraph)

    def _generate_graph_base_plot(self, title: str):
        """Helper method for single-data graph initialization

        Creates uplot.Plot object"""
        # TODO: add settings to this
        plot = Plot(x=5, y=-10,
                    width=235, height=140,
                    padding=20, show_box=False,
                    box_color=color.GRAY )

        font_file = r'.\fonts\roundedHeavy-26.bdf'
        font_to_use = bitmap_font.load_font(font_file)

        plot.show_text(title,
                       x=28, y=0,
                       anchorpoint=(0.0, 0.0),
                       text_color=color.GRAY,
                       free_text=True,
                       font=font_to_use, )

        # yah I know I'm not supposed to access protected members but I dont like full box
        # will check out uplot.Cartesian later
        plot._axesparams = 'cartesian'
        plot._drawbox()

        # Setting the tick parameters
        plot.tick_params(tickx_height=5, ticky_height=5,
                         show_ticks=True,
                         tickcolor=color.TEAL,
                         tickgrid=True,
                         showtext=True, )

        return plot
    #endregion



    def update_values(self, *, co2, temperature_c, humidity) -> None:
        """Update sensor values (and emoji, if relevant)."""
        self._co2 = co2
        self._temperature_c = temperature_c
        self._temperature_f = (temperature_c*9/5)+32
        self._humidity = humidity
        
        self._update_top_display_values()
        self._update_single_data_values()
        self._update_single_graph_values()

        # looks like we don't need this refresh.  display defaults to auto_refresh = True
        #self._display.refresh()
        
        
    def show_top_display(self) -> None:
        """Shows top-level display on screen."""
        self._display.root_group = self._group_top
        self._current_display_level = BotScreen._DisplayLevel.TOP
        
        
    def cycle_single_data_display(self) -> None:
        """Cycle between various sensors for single-sensor-value mode.

        This does not deal with data, only the change of display.  There are two
        actions this method is responsible for:
        1. Decide whether to cycle between sensors.  If not already in this mode, don't cycle.
           If already in this mode, move to next sensor.
        2. Set the display.root_group to show this single-data group
        """
        if self._current_display_level != BotScreen._DisplayLevel.SINGLE_DATA:  
            # we display previously shown single data display, don't cycle to next
            # no need to modify self._current_data_single_display
            pass
        else:
            # we are already at single data display, so cycle through sensors here
      
            self._current_single_data_sensor = next(BotScreen._single_data_display_states)
            # need to update fields,values since we are moving from currently selected sensor
            self._update_single_data_display_fixed_fields()
            self._update_single_data_values()
            
        self._current_display_level = BotScreen._DisplayLevel.SINGLE_DATA
        self._display.root_group = self._group_single_data

    def cycle_single_graph_display(self) -> None:
        """Cycle between various sensors for single-sensor-graph mode.

        This does not deal with data, only the change of display.  There are two
        actions this method is responsible for:
        1. Decide whether to cycle between sensors.  If not already in this mode, don't cycle.
           If already in this mode, move to next sensor.
        2. Set the display.root_group to show this graph group
        """
        if self._current_display_level != BotScreen._DisplayLevel.SINGLE_GRAPH:
            # we display previously shown single graph display, don't cycle to next
            # no need to switch to different graph
            pass
        else:
            # we are already at single graph display, so cycle through sensors here
            self._current_single_graph_sensor = next(BotScreen._single_graph_display_states)


        self._current_display_level = BotScreen._DisplayLevel.SINGLE_GRAPH

        display = self._graph_displays[self._current_single_graph_sensor]


        self._display.root_group = display.display_group


        
    def _update_top_display_values(self) -> None:
        """ Only need to update the data fields since the background is static"""
        
        self._group_top[BotScreen._FieldOrderTop.CO2].text = f'{self._co2: >4}'
        self._group_top[BotScreen._FieldOrderTop.HUMIDITY].text = f'{self._humidity:0.0f}%'
        
        # CircuitPython cannot do nested f-strings
        _ = f'{self._temperature_f:0.0f}{chr(176)}'
        self._group_top[BotScreen._FieldOrderTop.TEMPERATURE].text = f'{_: >4}'



    def _update_single_data_values(self) -> None:
        """Based on which sensor the user has selected, display those values, emoji"""
        state = self._current_single_data_sensor

        if state == BotScreen._Sensor.CO2:
            self._group_single_data[BotScreen._FieldOrderSingleData.DATA].text = f'{self._co2}'
            # for CO2, also have update emoji.
            self._group_single_data[BotScreen._FieldOrderSingleData.SPRITE_BLOB].hidden = False
            self._group_single_data[BotScreen._FieldOrderSingleData.SPRITE_BLOB][0] = self._get_emoji()

        elif state == BotScreen._Sensor.TEMPERATURE:
            self._group_single_data[BotScreen._FieldOrderSingleData.DATA].text = f'{self._temperature_f:0.0f}'
            self._group_single_data[BotScreen._FieldOrderSingleData.SPRITE_BLOB].hidden = True

        elif state == BotScreen._Sensor.HUMIDITY:
            self._group_single_data[BotScreen._FieldOrderSingleData.DATA].text = f'{self._humidity:0.0f}'
            self._group_single_data[BotScreen._FieldOrderSingleData.SPRITE_BLOB].hidden = True

        else:
            raise ValueError(f'Invalid state for display sensor mode: [{state}]')

    def _update_single_data_display_fixed_fields(self) -> None:
        """Updates the CO2, temp, or humidity symbol. Also updates units field.

       This needs to be done since currently, we are using only 1 displayio.group
       for all sensors.  Could switch this to separate displayio.groups for each sensor
       """
        state = self._current_single_data_sensor
        #print(f'{self._current_single_data_sensor=}')

        # we defined the sensor sprites in ._init_group_single_data().  So here we just choose
        # the appropriate sprite index (using the enum value from 'state'
        self._group_single_data[BotScreen._FieldOrderSingleData.SPRITE_SENSOR][0] = state   # enum value matches correct sprite index
        
        units = ['ppm', f'{chr(176)}F', '%']
        self._group_single_data[BotScreen._FieldOrderSingleData.UNITS].text = units[state]
    
    def _get_emoji(self) -> _BlobSprite:
        """Get specific emoji based on CO2 PPM value."""

        # TODO: move this range to settings file
        #       
        if self._co2 < 450:
            return BotScreen._BlobSprite.VERY_GOOD
            
        if self._co2 < 750:
            return BotScreen._BlobSprite.GOOD
        
        if self._co2 < 1000:
            return BotScreen._BlobSprite.OK
        
        if self._co2 < 1500:
            return BotScreen._BlobSprite.CONCERNING
        
        if self._co2 < 3000:
            return BotScreen._BlobSprite.UNHEALTHY
        
        if self._co2 < 5000:
            return BotScreen._BlobSprite.VERY_UNHEALTHY
        
        return BotScreen._BlobSprite.DANGER

    

    def _update_single_graph_values(self) -> None:
        self._update_single_graph(BotScreen._Sensor.CO2, self._co2)
        self._update_single_graph(BotScreen._Sensor.TEMPERATURE, self._temperature_f)
        self._update_single_graph(BotScreen._Sensor.HUMIDITY, self._humidity)
        """
        # CO2
        co2_display = self._graph_displays[BotScreen._Sensor.CO2]
        co2_group = co2_display.display_group
        co2_ulogger = co2_display.uplot_logging
        co2_x = co2_display.x
        co2_y = co2_display.y

        # x,y values needs to be added if we haven't yet filled up graph.
        # If you have filled up graph, then just update y-values so that graph scrolls
        if len(co2_x) < 120:
            next_x = len(co2_x) + 1
            co2_x.append(next_x)
            co2_y.insert(0, self._co2)
            #print(f'\n\n{co2_x=}\n{co2_y=}\n\n')
        else:
            # the x, y lists are at length 120 so just need to update y values so that plot scrolls
            co2_y.pop()
            co2_y.insert(0, self._co2)

        plot = co2_group[0]   # only the Plot object was appended to this group, so it is only element
        co2_ulogger.draw_points(plot = plot, x = co2_x, y = co2_y, fill = False)


        # temperature
        temperature_display = self._graph_displays[BotScreen._Sensor.TEMPERATURE]
        temperature_group = temperature_display.display_group
        temperature_ulogger = temperature_display.uplot_logging
        temperature_x = temperature_display.x
        temperature_y = temperature_display.y

        # x,y values needs to be added if we haven't yet filled up graph.
        # If you have filled up graph, then just update y-values so that graph scrolls
        if len(temperature_x) < 120:
            next_x = len(temperature_x) + 1
            temperature_x.append(next_x)
            temperature_y.insert(0, self._temperature_f)
            #print(f'\n{temperature_x=}\n{temperature_y=}')
        else:
            # the x, y lists are at length 120 so just need to update y values so that plot scrolls
            temperature_y.pop()
            temperature_y.insert(0, self._temperature_f)

        plot = temperature_group[0]  # only the Plot object was appended to this group
        temperature_ulogger.draw_points(plot=plot, x=temperature_x, y=temperature_y, fill=False)


        # humidity
        humidity_display = self._graph_displays[BotScreen._Sensor.HUMIDITY]
        humidity_group = humidity_display.display_group
        humidity_ulogger = humidity_display.uplot_logging
        humidity_x = humidity_display.x
        humidity_y = humidity_display.y

        # x,y values needs to be added if we haven't yet filled up graph.
        # If you have filled up graph, then just update y-values so that graph scrolls
        if len(humidity_x) < 120:
            next_x = len(humidity_x) + 1
            humidity_x.append(next_x)
            humidity_y.insert(0, self._humidity)
        else:
            # the x, y lists are at length 120 so just need to update y values so that plot scrolls
            humidity_y.pop()
            humidity_y.insert(0, self._humidity)

        plot = humidity_group[0]  # only the Plot object was appended to this group
        humidity_ulogger.draw_points(plot=plot, x=humidity_x, y=humidity_y, fill=False)
        """

    def _update_single_graph(self, sensor: BotScreen._Sensor, sensor_value: int|float) -> None:
        sensor_display = self._graph_displays[sensor]  # get the respective graph object
        display_group = sensor_display.display_group
        ulogger = sensor_display.uplot_logging
        x = sensor_display.x
        y = sensor_display.y

        # x,y values needs to be added if we haven't yet filled up graph.
        # If you have filled up graph, then just update y-values so that graph scrolls
        if len(x) < 120:
            next_x = len(x) + 1
            x.append(next_x)
            y.insert(0, self._humidity)
        else:
            # the x, y lists are at length 120 so just need to update y values so that plot scrolls
            y.pop()
            y.insert(0, self._humidity)

        plot = display_group[0]  # only the Plot object was appended to this group
        ulogger.draw_points(plot=plot, x=x, y=y, fill=False)

