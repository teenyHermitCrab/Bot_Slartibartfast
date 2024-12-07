from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label,  wrap_text_to_lines   #######
import adafruit_imageload        ##
from adafruit_itertools import cycle
import board
import displayio
# local imports below
from enum import Enum  # no builtin Enum in circuitpython, so this is a hack
   

class BotScreen:
    """There is not a huge amount of space for bitmaps, fonts.  So this first iteration is using sprites to share bitmap space 
    across the main display modes.  A bit more complicated to modify a display when switching sensors, 
    
    Otherwise, we would have more TileGroups vs sprites, but that might be easier for code maintenance if adding a bunch of 
    extra display modes.  
        
    
    TODO: add usage notes
    """
    
    _DisplayLevel = Enum(TOP           = 0,    # all data fields
                         SINGLE_DATA   = 1, 
                         SINGLE_GRAPH  = 2,)

    _Sensor = Enum(CO2         = 0,
                   TEMPERATURE = 1,
                   HUMIDITY    = 2,)
        
    _BlobSprite = Enum(VERY_GOOD      = 0,
                       GOOD           = 1,
                       OK             = 2,
                       CONCERNING     = 3,
                       UNHEALTHY      = 4,
                       VERY_UNHEALTHY = 5,
                       DANGER         = 6,)
    
    
    #These are the order of group appends when constructing the top-level display
    _FieldOrderTop = Enum(CO2         = 1,
                          TEMPERATURE = 3,
                          HUMIDITY    = 4,)
        
    _FieldOrderSingleData = Enum(SPRITE_SENSOR = 0,
                                 SPRITE_BLOB   = 1,
                                 DATA          = 2,
                                 UNITS         = 3,)
                                 
    #_FieldOrderSingleGraph = Enum(....)
    
    _single_data_display_states = cycle([_Sensor.CO2, _Sensor.TEMPERATURE, _Sensor.HUMIDITY])
    #_single_graph_display_states = cycle([_Sensor.CO2, _Sensor.TEMPERATURE, _Sensor.HUMIDITY])

    
    def __init__(self, settings = None):
        """First iteration: dont worry about making this too general.  Just use as 
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
        
        self._group_top = self._init_group_top(settings)
        self._group_single_data = self._init_group_single_data(settings)
        
        self._display = board.DISPLAY
        self._display.root_group = self._group_top
        
        self._current_display_level = BotScreen._DisplayLevel.TOP
        self._current_single_data_display = next(BotScreen._single_data_display_states)
        #self._current_single_graph_display = next(_single_graph_display_states)
        
        
    def _init_group_top(self, settings):
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
        
        # this append order matters since the first element 'tile_grid_top' is a background, so it needs to be first
        # other elements (Label objects) could be in any order since they dont overlap, but keep this order so we can 
        # reference the text values by append order. I.e., append in order of _TextOrderTopLevel
        group_top.append(tile_grid_top)
        group_top.append(co2_label) 
        group_top.append(co2_units_label)
        group_top.append(temperature_label)
        group_top.append(humidity_label)
        
        return group_top
        
        
    def _init_group_single_data(self, settings):
        # TODO: decide whether these go to a settings file.  That would probably make it easier to use different displays
        #       If so, may want to store percentage in settings file? then could have a helper method (knowing display resolution)
        #       that could translate to x,y values
        
        font_file = r".\fonts\Arial-Bold-36.bdf"
        font_value = bitmap_font.load_font(font_file)
            
        font_file = r".\fonts\LeagueSpartan-Bold-16.bdf"
        font_units = bitmap_font.load_font(font_file)
        
        data_label = bitmap_label.Label(font_value, text='8888', 
                                              color=0xFFFFFF, scale=1,
                                              anchor_point = (1.0, 0.0), anchored_position = (160, 80))
        unit_label = bitmap_label.Label(font_units, text='ppm', 
                                        color=0xFFFFFF, scale=1,
                                        anchor_point = (0.0, 0.0), anchored_position = (170, 80)) 
         
        # we dont need an explicit black background, since display is already black when pixels are off
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
        # this append order matters since the first element 'tile_grid_top' is a background, so it needs to be first
        # other elements (Label objects) could be in any order since they dont overlap, but keep this order so we can 
        # reference the text values by append order. I.e., append in order of _TextOrderTopDisplay
        group_single_display.append(sprite_sensor)
        group_single_display.append(sprite_blob)
        group_single_display.append(data_label)
        group_single_display.append(unit_label)
        
        return group_single_display
        
        
    def update_values(self, *, co2, temperature_c, humidity) -> None:
        self._co2 = co2
        self._temperature_c = temperature_c
        self._temperature_f = (temperature_c*9/5)+32
        self._humidity = humidity
        
        self._update_top_display_values()
        self._update_single_data_display_values()
        #self._update_single_graph_display_values()
        
        
    def show_top_display(self) -> None:
        self._display.root_group = self._group_top
        self._current_display_level = BotScreen._DisplayLevel.TOP
        
        
    def cycle_single_data_display(self) -> None:
        """This does not deal with data, only the change of display"""
        
        if self._current_display_level != BotScreen._DisplayLevel.SINGLE_DATA:  
            # we display previously shown single data display, dont cycle to next
            
            # no need to modify self._current_data_single_display
            pass
        else:
            # we are already at single data display, so cycle through sensors here
      
            self._current_single_data_display = next(BotScreen._single_data_display_states)
            # need to update fields,values since we are moving from currently selected sensor
            self._update_single_data_display_fixed_fields()
            self._update_single_data_display_values()
            
        self._current_display_level = BotScreen._DisplayLevel.SINGLE_DATA
        self._display.root_group = self._group_single_data
            
        
    def _update_top_display_values(self) -> None:
        """ Only need to update the data fields since the background is static"""
        
        self._group_top[BotScreen._FieldOrderTop.CO2].text = f'{self._co2: >4}'
        self._group_top[BotScreen._FieldOrderTop.HUMIDITY].text = f'{self._humidity:0.0f}%'
        
        # circuitpython canna do nested f-strings 
        _ = f'{self._temperature_f:0.0f}{chr(176)}'
        self._group_top[BotScreen._FieldOrderTop.TEMPERATURE].text = f'{_: >4}'
        
        
    def _update_single_data_display_fixed_fields(self) -> None:
        state = self._current_single_data_display
        #print(f'{self._current_single_data_display=}')
                
        self._group_single_data[BotScreen._FieldOrderSingleData.SPRITE_SENSOR][0] = state   # enum value matches correct sprite index
        
        units = ['ppm', f'{chr(176)}F', '%']
        self._group_single_data[BotScreen._FieldOrderSingleData.UNITS].text = units[state]
        
        
    def _update_single_data_display_values(self) -> None:
        # test for current sensor, update values, update emoji if needed
        state = self._current_single_data_display
        
        if state == BotScreen._Sensor.CO2:
            self._group_single_data[BotScreen._FieldOrderSingleData.DATA].text = f'{self._co2}'
            # for CO2, also have update emoji
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
        
    
    def _get_emoji(self) -> _BlobSprite:
        
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
    
    
    
    
    """  
    def _update_single_graph_display_fixed_fields(self) -> None:
        pass  
    def _update_single_graph_display_values(self) -> None:
        pass
    """ 
        
        
        
        
        
        
        
        
        
        
