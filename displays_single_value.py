from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label
import adafruit_imageload
from adafruit_itertools import cycle
import displayio
from enum import Enum

Sensors = Enum('CO2', 'TEMPERATURE', 'HUMIDITY')
Emoji = Enum('VERY_GOOD', 'GOOD', 'OK', 'CONCERNING', 'UNHEALTHY', 'VERY_UNHEALTHY', 'DANGER')

# Index of group appends for single data mode screen
# This is not a great system - if data groups get complicated enough to outgrow this, then just make them their own classes
FieldOrder = Enum(SPRITE_SENSOR = 0,
                  DATA          = 1,
                  UNITS         = 2,
                  SPRITE_EMOJI  = 3, )



class DisplaySingleValue:
    """Class to wrap displays where only a single sensor is being displayed."""

    _single_value_display_sensors = cycle([Sensors.CO2, Sensors.TEMPERATURE, Sensors.HUMIDITY])

    def __init__(self, root_display: displayio.Display):
        self._root = root_display  # need a reference to actual screen display when we are switching graphs on screen
        settings = None  #
        self._sensor_groups: list[displayio.Group] = [self._init_display_group_co2(settings),
                                                      self._init_display_group_temp(settings),
                                                      self._init_display_group_humidity(settings), ]

        # keeping the cycle iterator on the index to allow me index into GraphStruct objects.
        # If I didn't have a separate update values method, then probably could just cycle through graph displays directly
        self._current_sensor_idx = next(DisplaySingleValue._single_value_display_sensors)

    def _load_settings(self):
        return None


    #region initialize sensor displayio.groups
    def _init_display_group_co2(self, settings) -> displayio.Group:
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
                                        anchor_point=(1.0, 0.0), anchored_position=(90, 80))
        unit_label = bitmap_label.Label(font_units, text='ppm',
                                        color=0xFFFFFF, scale=1,
                                        anchor_point=(0.0, 0.0), anchored_position=(100, 80))

        # we don't need an explicit black background, since display is already black when pixels are off
        # bitmap_black_background = displayio.OnDiskBitmap(r".\bitmaps\black_background.bmp")
        # tile_grid_background = displayio.TileGrid(bitmap_black_background,
        #                                          pixel_shader=bitmap_black_background.pixel_shader)

        # Load the sprite sheet for sensor symbols
        sprite_sheet1, palette1 = adafruit_imageload.load(r".\bitmaps\sensor_symbols_sprite_210x70.bmp",
                                                          bitmap=displayio.Bitmap,
                                                          palette=displayio.Palette)
        # Create a sprite for sensor symbol
        sprite_sensor = displayio.TileGrid(sprite_sheet1, pixel_shader=palette1,
                                           width=1, height=1,
                                           x=160, y=5,
                                           tile_width=70, tile_height=70)
        sprite_sensor[0] = Sensors.CO2

        sprite_sheet2, palette2 = adafruit_imageload.load(r".\bitmaps\blobs_black_background_680x80.bmp",
                                                          bitmap=displayio.Bitmap,
                                                          palette=displayio.Palette)
        sprite_emoji = displayio.TileGrid(sprite_sheet2, pixel_shader=palette2,
                                          width=1, height=1,
                                          x=5, y=5,
                                          tile_width=85, tile_height=80)

        group_single_display = displayio.Group(scale=1)
        # Append order matters - it is z-order on displays.  We also can use this to access labels or sprites
        group_single_display.append(sprite_sensor)
        group_single_display.append(data_label)
        group_single_display.append(unit_label)
        group_single_display.append(sprite_emoji)

        return group_single_display

    def _init_display_group_temp(self, settings) -> displayio.Group:
        """Initialize display for single-data mode temperature"""

        font_file = r".\fonts\Arial-Bold-36.bdf"
        font_value = bitmap_font.load_font(font_file)

        font_file = r".\fonts\LeagueSpartan-Bold-16.bdf"
        font_units = bitmap_font.load_font(font_file)

        data_label = bitmap_label.Label(font_value, text='--',
                                        color=0xFFFFFF, scale=2,
                                        anchor_point=(1.0, 1.0), anchored_position=(120, 90))
        unit_label = bitmap_label.Label(font_units, text='°F',
                                        color=0xFFFFFF, scale=2,
                                        anchor_point=(0.0, 1.0), anchored_position=(125, 80))

        # Load the sprite sheet for sensor symbols
        sprite_sheet1, palette1 = adafruit_imageload.load(r".\bitmaps\sensor_symbols_sprite_210x70.bmp",
                                                          bitmap=displayio.Bitmap,
                                                          palette=displayio.Palette)
        # Create a sprite for sensor symbol
        sprite_sensor = displayio.TileGrid(sprite_sheet1, pixel_shader=palette1,
                                           width=1, height=1,
                                           x=160, y=5,
                                           tile_width=70, tile_height=70)
        sprite_sensor[0] = Sensors.TEMPERATURE

        group_single_display = displayio.Group(scale=1)
        # Append order matters - it is z-order on displays.  We also can use this to access labels or sprites
        group_single_display.append(sprite_sensor)
        group_single_display.append(data_label)
        group_single_display.append(unit_label)

        return group_single_display

    def _init_display_group_humidity(self, settings) -> displayio.Group:
        """Initialize display for single-data mode temperature"""

        font_file = r".\fonts\Arial-Bold-36.bdf"
        font_value = bitmap_font.load_font(font_file)

        font_file = r".\fonts\LeagueSpartan-Bold-16.bdf"
        font_units = bitmap_font.load_font(font_file)

        data_label = bitmap_label.Label(font_value, text='--',
                                        color=0xFFFFFF, scale=2,
                                        anchor_point=(1.0, 1.0), anchored_position=(120, 90))
        unit_label = bitmap_label.Label(font_units, text='%',
                                        color=0xFFFFFF, scale=2,
                                        anchor_point=(0.0, 1.0), anchored_position=(125, 80))

        # Load the sprite sheet for sensor symbols
        sprite_sheet1, palette1 = adafruit_imageload.load(r".\bitmaps\sensor_symbols_sprite_210x70.bmp",
                                                          bitmap=displayio.Bitmap,
                                                          palette=displayio.Palette)
        # Create a sprite for sensor symbol
        sprite_sensor = displayio.TileGrid(sprite_sheet1, pixel_shader=palette1,
                                           width=1, height=1,
                                           x=160, y=5,
                                           tile_width=70, tile_height=70)
        sprite_sensor[0] = Sensors.HUMIDITY

        group_single_display = displayio.Group(scale=1)
        # Append order matters - it is z-order on displays.  We also can use this to access labels or sprites
        group_single_display.append(sprite_sensor)
        group_single_display.append(data_label)
        group_single_display.append(unit_label)



        return group_single_display

    # TODO: make a helper method for display group initializers - there is alot of repeated code here
    #endregion


    #region update values
    def update_values(self, *, co2: int, temperature_f: float, humidity: float) -> None:
        """Updates all the sensor groups, regardless if they are being shown on screen"""

        # if the display groups were really complicated, they could be their own classes to handle complex updates.

        group = self._sensor_groups[Sensors.CO2]
        # noinspection PyUnresolvedReferences
        group[FieldOrder.DATA].text = f'{co2: >4}'
        group[FieldOrder.SPRITE_EMOJI][0] = self._get_emoji_co2(co2)

        group = self._sensor_groups[Sensors.TEMPERATURE]
        # noinspection PyUnresolvedReferences
        group[FieldOrder.DATA].text = f'{temperature_f:0.0f}'

        group = self._sensor_groups[Sensors.HUMIDITY]
        # noinspection PyUnresolvedReferences
        group[FieldOrder.DATA].text = f'{humidity:0.0f}'


    def _get_emoji_co2(self, ppm: int) -> Emoji:
        """Get specific emoji based on CO2 PPM value."""

        # TODO: move this range to settings file
        #
        # CircuitPython does not yet have match/case syntax
        if ppm < 450:
            return Emoji.VERY_GOOD
        if ppm < 750:
            return Emoji.GOOD
        if ppm < 1000:
            return Emoji.OK
        if ppm < 1500:
            return Emoji.CONCERNING
        if ppm < 3000:
            return Emoji.UNHEALTHY
        if ppm < 5000:
            return Emoji.VERY_UNHEALTHY
        return Emoji.DANGER
    #endregion


    def cycle_data_display(self, cycle_prior_to_display:bool = False) -> None:
        """Cycle between various sensors for single-sensor-value mode.

        This does not deal with data, only the change of display.  There are two
        actions this method is responsible for:
        1. Decide whether to cycle between sensors.  If not already in this mode, don't cycle.
           If already in this mode, move to next sensor.
        2. Set the display.root_group to show this single-data group
        """
        if not cycle_prior_to_display:
            # display previously shown graph display, don't cycle to next - no need to switch to different graph
            pass
        else:
            # we are already at a graph display, so cycle through sensors here
            self._current_sensor_idx = next(DisplaySingleValue._single_value_display_sensors)

        group = self._sensor_groups[self._current_sensor_idx]
        # recall assigning to root_group is what actually puts this on physical screen
        self._root.root_group = group