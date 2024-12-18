import time
from adafruit_bitmap_font import bitmap_font
from adafruit_itertools import cycle
from circuitpython_uplot.plot import Plot, color
from circuitpython_uplot.logging import Logging as Ulogging
import displayio
from enum import Enum


class GraphStruct:
    """Class to wrap related objects and data for distinct graph displays.

    We need a structure for the graphing displays.
    The single-data value displays are simple enough to just use a displayio.Group object

    # QUESTION: does CircuitPython have dataclasses module in bundles?

    Contains:
    - Display group. This is what gets assigned to root_group (which shows it on screen)
    - uplot logging object.  This is what updates new data to plot.  It is not a debug logger
    - x, y previous data.  The plot doesn't save previous x,y data.  It is just a drawing.
      We need the previous data when adding new points.
    """

    def __init__(self, group: displayio.Group, ulog: Ulogging, x: list[int]=None, y: list[int|float]=None):
        self.display_group = group
        self.uplot_logging = ulog
        # uplot logging doesn't actually save the x,y points, it just draws on the plot
        # so save previous points, since we need to update this list when new data arrives
        if x is None:
            self.x = []
        if y is None:
            self.y = []

Sensors = Enum('CO2', 'TEMPERATURE', 'HUMIDITY')


class DisplayGraphs:

    _graph_display_sensors = cycle([Sensors.CO2, Sensors.TEMPERATURE, Sensors.HUMIDITY])

    def __init__(self, root_display: displayio.Display):
        self._root = root_display   # need a reference to actual screen display when we are switching graphs on screen
        self._graph_displays: list[GraphStruct] = [self._init_display_co2(),
                                                   self._init_display_temp(),
                                                   self._init_display_humidity(), ]

        # keeping the cycle iterator on the index to allow me index into GraphStruct objects.
        # If I didn't have a separate update values method, then probably could just cycle through graph displays directly
        self._current_graph_sensor_idx = next(DisplayGraphs._graph_display_sensors)

        # average any values received (over this interval) before adding to graph
        self._graph_interval_seconds: int = 60
        self._co2_interval_values: list[int] = []
        self._temperature_interval_values: list[float] = []
        self._humidity_interval_values: list[float] = []
        self._interval_start_time = time.monotonic()


    # region initialize graph displays
    def _init_display_co2(self) -> GraphStruct:
        """Initialize CO2 display

        Creates display group, uplot logging, x/y data storage
        """
        # TODO: add settings
        plot = self._generate_graph_base_plot(title='CO2')

        g = displayio.Group()
        g.append(plot)

        my_loggraph = Ulogging(plot=plot,
                               x=[], y=[],
                               rangex=[120, 0], rangey=[0, 2500],
                               line_color=color.YELLOW,
                               ticksx=[120, 100, 80, 60, 40, 20, 0, ],
                               ticksy=[300, 650, 1000, 1750, 2500],
                               tick_pos=False,
                               # limits=[1000, 1750, ],   # limit lines clutter the small 240x135 screen
                               fill=True)

        return GraphStruct(group=g, ulog=my_loggraph)

    def _init_display_temp(self) -> GraphStruct:
        """Initialize temperature graph

        Creates display group, uplot logging, x/y data storage
        """
        # TODO: add settings
        plot = self._generate_graph_base_plot(title='°F')

        g = displayio.Group()
        g.append(plot)

        my_loggraph = Ulogging(plot=plot,
                               x=[], y=[],
                               rangex=[120, 0], rangey=[30, 110],
                               line_color=color.YELLOW,
                               ticksx=[120, 100, 80, 60, 40, 20, 0, ],
                               ticksy=[50, 70, 80, 90, 110],
                               tick_pos=False,
                               # limits=[60, 100, ],    # limit lines clutter the small 240x135 screen
                               fill=True)

        return GraphStruct(group=g, ulog=my_loggraph)

    def _init_display_humidity(self) -> GraphStruct:
        """Initialize humidity graph

        Creates display group, uplot logging, x/y data storage
        """
        # TODO: add settings
        plot = self._generate_graph_base_plot(title='rH %')

        g = displayio.Group()
        g.append(plot)

        my_loggraph = Ulogging(plot=plot,
                               x=[], y=[],
                               rangex=[120, 0], rangey=[0, 100],
                               line_color=color.YELLOW,
                               ticksx=[120, 100, 80, 60, 40, 20, 0, ],
                               ticksy=[20, 40, 60, 80, 100],
                               tick_pos=False,
                               ## limit lines clutter the small 240x135 screen
                               #limits=[20, 65, ],
                               fill=True)

        return GraphStruct(group=g, ulog=my_loggraph)

    @staticmethod
    def _generate_graph_base_plot(title: str) -> Plot:
        """Helper method for single-data graph initialization

        Creates uplot.Plot object"""
        # TODO: add settings to this
        plot = Plot(x=5, y=-10,
                    width=235, height=140,
                    padding=20, show_box=False,
                    box_color=color.GRAY)

        font_file = r'.\fonts\roundedHeavy-26.bdf'
        font_to_use = bitmap_font.load_font(font_file)

        plot.show_text(title,
                       x=28, y=0,
                       anchorpoint=(0.0, 0.0),
                       text_color=color.GRAY,
                       free_text=True,
                       font=font_to_use, )


        plot._axesparams = 'cartesian'
        # yah I know I'm not supposed to access protected members, but I don't like full box
        # will check out uplot.Cartesian later, I believe that does support only 2 axes.
        # another thing to investigate: extend uplot to add ticks to both sides
        plot._drawbox()

        # Setting the tick parameters
        plot.tick_params(tickx_height=5, ticky_height=5,
                         show_ticks=True,
                         tickcolor=color.TEAL,
                         tickgrid=True,
                         showtext=True, )

        return plot
    # endregion


    # region update values
    def update_values(self, *, co2: int, temperature_f: float, humidity: float) -> None:
        """Updates plots on each display, regardless if they are being shown on screen.

        Adds values to interval buffer.  If interval expires, then actually update graphs with average value

        :param co2: CO2 value in ppm.
        :param temperature_f: Temperature value in °F
        :param humidity: Relative humidity in %
        """

        # TODO: this works for now, but the interval check should really be on a separate task
        #
        if (time.monotonic() - self._interval_start_time) >= self._graph_interval_seconds:
            if len(self._co2_interval_values) > 0:
                avg_co2 = sum(self._co2_interval_values) / len(self._co2_interval_values)
                display: GraphStruct = self._graph_displays[Sensors.CO2]
                self._update_single_graph(display, avg_co2)
                self._co2_interval_values = []

            if len(self._temperature_interval_values) > 0:
                avg_temperature = sum(self._temperature_interval_values) / len(self._temperature_interval_values)
                display: GraphStruct = self._graph_displays[Sensors.TEMPERATURE]
                self._update_single_graph(display, avg_temperature)
                self._temperature_interval_values = []

            if len(self._humidity_interval_values) > 0:
                avg_humidity = sum(self._humidity_interval_values) / len(self._humidity_interval_values)
                display: GraphStruct = self._graph_displays[Sensors.HUMIDITY]
                self._update_single_graph(display, avg_humidity)
                self._humidity_interval_values = []

            self._interval_start_time = time.monotonic()

        self._co2_interval_values.append(co2)
        self._temperature_interval_values.append(temperature_f)
        self._humidity_interval_values.append(humidity)



    @staticmethod
    def _update_single_graph(display: GraphStruct, sensor_value: int | float) -> None:
        """Helper method to update single-sensor graph displays"""
        display_group = display.display_group
        ulogger = display.uplot_logging
        x = display.x
        y = display.y

        # x,y values needs to be added if we haven't yet filled up graph.
        # If you have filled up graph, then just update y-values so that graph scrolls
        if len(x) < 120:
            next_x = 120 - len(x)   # counting down from 120, since y-axis is labelled 120 ----> 0
            x.append(next_x)
            y.append(sensor_value)
        else:
            # the x, y lists are at length 120 so just need to update y values so that plot scrolls
            y.pop()
            y.insert(0, sensor_value)

        plot = display_group[0] # only the Plot object was appended to this group

        # noinspection PyTypeChecker
        ulogger.draw_points(plot=plot, x=x, y=y, fill=False)
    # endregion


    def cycle_graph_display(self, cycle_prior_to_display:bool = False) -> None:
        """Cycle between various sensors for single-sensor-graph mode.

        This does not deal with data, only the change of display.  There are two
        actions this method is responsible for:
        1. Decide whether to cycle between sensors.  If not already in this mode, don't cycle - this will serve to
           remember which graph you had previously viewed.
              - If already in this mode, move to next sensor.
        2. Set the display.root_group to show this graph group
        """

        if cycle_prior_to_display:
            # we are already at a graph display, so cycle through sensors here
            self._current_graph_sensor_idx = next(DisplayGraphs._graph_display_sensors)

        display = self._graph_displays[self._current_graph_sensor_idx]
        # recall assigning to root_group is what actually puts this on physical screen
        self._root.root_group = display.display_group
