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
from display_top_level import AllValuesDisplay
from displays_single_value import DisplaySingleValue
from displays_graphing import DisplayGraphs
   

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

    # NOTE: using enum hack is kinda shiny, but then have to specify full name. E.g.:,  BotScreen._DisplayLevel.ALL_VALUES.
    #       so kinda wordy.  Could just use an internal class here.  At least using Enum makes it
    #       clear what we are doing

    # using class allows PyCharm to populate...
    class DisplayLevel:
        ALL_VALUES = 0
        SINGLE_DATA = 1
        SINGLE_GRAPH = 2





    
    def __init__(self, settings = None):
        """First iteration: don't worry about making this too general.  Just use as
           a spot to keep code out of code.py or robot level
        """

        self._display = board.DISPLAY  # we may want to address another screen

        # They are assigned to display.root_group to show on screen
        self._display_all_values = AllValuesDisplay(board.DISPLAY)
        self._displays_single_value = DisplaySingleValue(board.DISPLAY)
        self._displays_graphs = DisplayGraphs(board.DISPLAY)

        self._current_display_level = BotScreen.DisplayLevel.ALL_VALUES
        # not the actual display, just which sensor is current


        self._display_all_values.show_on_screen()





    def update_values(self, *, co2: int|float, temperature_c: float, humidity: float) -> None:
        """Update sensor values (and emoji, if relevant)."""
        temperature_f = (temperature_c*9/5)+32

        self._display_all_values.update_values(co2=int(co2), temperature_f=temperature_f, humidity=humidity)
        self._displays_single_value.update_values(co2=int(co2), temperature_f=temperature_f, humidity=humidity)
        self._displays_graphs.update_values(co2=int(co2), temperature_f=temperature_f, humidity=humidity)

        # looks like we don't need this refresh.  display defaults to auto_refresh = True
        #self._display.refresh()
        
        
    def show_top_display(self) -> None:
        """Shows top-level display on screen."""
        self._display_all_values.show_on_screen()
        self._current_display_level = BotScreen.DisplayLevel.ALL_VALUES


    def show_single_value_display(self):
        switch_to_next = self._current_display_level == BotScreen.DisplayLevel.SINGLE_DATA
        self._displays_single_value.cycle_data_display(switch_to_next)
        self._current_display_level = BotScreen.DisplayLevel.SINGLE_DATA


    def show_single_graph_display(self):
        switch_to_next = self._current_display_level == BotScreen.DisplayLevel.SINGLE_GRAPH
        self._displays_graphs.cycle_graph_display(switch_to_next)
        self._current_display_level = BotScreen.DisplayLevel.SINGLE_GRAPH

