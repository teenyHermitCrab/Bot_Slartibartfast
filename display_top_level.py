from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label
import displayio
from enum import Enum

FieldOrderData = Enum(CO2         = 1,
                      TEMPERATURE = 3,
                      HUMIDITY    = 4, )

class AllValuesDisplay:
    def __init__(self, root_display: displayio.Display):
        self._root = root_display  # need a reference to actual screen display when we are switching graphs on screen
        settings = None  #
        self._display_group = self._init_group_top(settings)




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
        # ppm units label is makes it too long to display all value on this tiny 240x135 display
        # so putting it below CO2 value
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

    def update_values(self, *, co2: int, temperature_f: float, humidity: float) -> None:
        """ Only need to update the data fields since the background is static"""
        # noinspection PyUnresolvedReferences
        self._display_group[FieldOrderData.CO2].text = f'{co2: >4}'

        # CircuitPython cannot do nested f-strings
        _ = f'{temperature_f:0.0f}{chr(176)}'
        # noinspection PyUnresolvedReferences
        self._display_group[FieldOrderData.TEMPERATURE].text = f'{_: >4}'

        # noinspection PyUnresolvedReferences
        self._display_group[FieldOrderData.HUMIDITY].text = f'{humidity:0.0f}%'



    def show_on_screen(self) -> None:
        self._root.root_group = self._display_group