#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for visualizing messages.
"""


from typing import Optional, Union

import calmap
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .. import parse
from ..analysis import emojis


class WeekdayRadialHeatmap:
    """Class to create a radial heatmap of text message frequency.
    
    The radial heatmap has 24 slices (1 for each hour of the day) and 7 layers
    (1 for each day of the week). Each cell of the heatmap is then colored
    according to the specified colormap, with color intensity determined by
    the frequency of text messages during that day and time.
    """

    _DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
             'Friday', 'Saturday']

    def __init__(self, data: pd.DataFrame):
        """Initializes the WeekdayRadialHeatmap object."""

        # Store instance variables
        self._data = data
        
        # Construct the frequency matrix
        self._matrix_df = self._construct_frequency_matrix(self._data)
        self._matrix = self._matrix_df.to_numpy()

    def generate(self,
            figsize: tuple[int, int]=(7, 7),
            cmap: Union[str, mpl.colors.Colormap]='viridis',
            outline_color: str='black',
            grid_color: str='black',
            weekday_color: str='black',
            hour_color: str='black',
            font_name: 'str'='Helvetica',
            font_size: float=10,
            donut_hole: bool=True,
            donut_radius: float=0.5,
            show_weekdays: bool=True,
            show_hours: bool=True,
            show_outline: bool=True,
            show_grid: bool=True,
            cbar: bool=False,
            cbar_location: Optional[str]='vertical',
            cbar_shrink: float=1.0,
            cbar_padding: Optional[float]=None,
            cbar_aspect: float=20,
            cbar_label: Optional[str]=None,
            cbar_text_color: str='black',
            cbar_tick_color: str='black',
            cbar_outline_color: str='black',
            cbar_outline_linewidth: float=1,
            cbar_title: Optional[str]=None,
            cbar_minorticks: bool=False,
        ):
        """Generates the radial heatmap."""

        # Set method constants
        SLICES = 24
        LAYERS = 7

        # Create arrays and then a meshgrid from those arrays
        radius = np.linspace(1, LAYERS, LAYERS)
        azimuth = np.linspace(0, 2*np.pi, SLICES, endpoint=False)
        r, theta = np.meshgrid(radius, azimuth)

        # Create the figure and axis as a polar projection
        self.figure, self.axis = plt.subplots(
            subplot_kw={'projection': 'polar'},
            figsize=figsize,
        )

        # Create a color mesh that functions as the heatmap
        color_mesh = self.axis.pcolormesh(
            theta, r, self._matrix, shading='nearest', cmap=cmap
        )

        # Create the theta gridlines
        thetas = [t * 360//SLICES for t in range(SLICES)]
        hours = [self._military_to_standard(h) for h in range(1, SLICES+1)]
        self.axis.set_thetagrids(thetas, hours)

        # Reverse the positive theta direction
        self.axis.set_theta_direction(-1)

        # Offset the theta starting point
        slice_degrees = 360 / SLICES
        theta_offset = np.radians(90 - (3/2)*slice_degrees)
        self.axis.set_theta_offset(theta_offset)

        # Create the radial gridlines
        self.axis.set_rgrids(
            [i+0.5 for i in range(0, LAYERS+1)],
            ['']+self._DAYS
        )

        # Rotate and orient the hour labels
        if show_hours:
            x_ticks = zip(self.axis.get_xticklabels(), thetas)
            for i, (tick, angle) in enumerate(x_ticks, start=1):
                x, y = tick.get_position()
                label = self.axis.text(
                    x, y+0.025,
                    tick.get_text(), transform=tick.get_transform(),
                    ha=tick.get_ha(), va=tick.get_va(),
                    fontsize=font_size, fontname=font_name,
                )
                label.set_rotation(self._rotate_text(i, angle, slice_degrees))
                label.set_color(hour_color)

        # Rotate and orient the weekday labels
        if show_weekdays:
            y_ticks = zip(self.axis.get_yticklabels(), thetas)
            for tick, angle in y_ticks:
                x, y = tick.get_position()
                label = self.axis.text(
                    x, y-0.500,
                    tick.get_text()[:3], transform=tick.get_transform(),
                    ha='center', va='center',
                    fontsize=font_size, fontname=font_name,
                )
                label.set_rotation(-45)
                label.set_color(weekday_color)
        
        # Turn off tick labels because they were replaced with text annotations
        self.axis.set_xticklabels([])
        self.axis.set_yticklabels([])

        # Customize spines
        self.axis.spines['polar'].set_color(outline_color)
        self.axis.spines['polar'].set_visible(show_outline)

        # Turn on the grid if desired
        if show_grid:
            self.axis.yaxis.grid(True, color=grid_color, alpha=0.25)

        # Plot the data
        self.axis.plot(azimuth, r, ls='none', color='k')

        # Add a donut hole if desired
        if donut_hole:
            patch = mpl.patches.Circle(
                (0, 0), radius=donut_radius, fill=False, alpha=0,
            )
            self.axis.add_patch(patch)
        
        # Create and customize a colorbar if desired
        if cbar:
            if not cbar_padding:
                cbar_padding = 0.05 if cbar_location == 'vertical' else 0.15
            self.colorbar = self.figure.colorbar(
                color_mesh,
                ax=self.axis,
                shrink=cbar_shrink,
                pad=cbar_padding,
                location=cbar_location,
                aspect=cbar_aspect,
            )
            self.colorbar.outline.set_color(cbar_outline_color)
            self.colorbar.outline.set_linewidth(cbar_outline_linewidth)
            if cbar_minorticks:
                self.colorbar.minorticks_on()
            if cbar_label:
                self.colorbar.set_label(
                    cbar_label, color=cbar_text_color, fontsize=font_size,
                )
            if cbar_title:
                self.colorbar.ax.set_title(
                    cbar_title, color=cbar_text_color, fontsize=font_size,
                )
            self.colorbar.ax.xaxis.set_tick_params(
                color=cbar_outline_color, labelcolor=cbar_tick_color,
            )
            self.colorbar.ax.yaxis.set_tick_params(
                color=cbar_outline_color, labelcolor=cbar_tick_color,
            )
        else:
            self.colorbar = None
    
    def save(self, *args, **kwargs):
        """Wrapper around plt.savefig()."""
        plt.savefig(*args, **kwargs)
    
    def show(self):
        """Wrapper around plt.show()."""
        plt.show()

    def _construct_frequency_matrix(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Takes Messages object data and converts it into a usable matrix form
        which contains text message frequency information for each hour of
        each day of the week.
        """

        # Group the data by weekday and then by hour, and count frequencies
        grouped = data['message'].groupby(
            [data.index.day_name(), data.index.hour]
        ).count()
        
        # Create a dataframe from the grouped data
        matrix = pd.DataFrame({day: grouped.get(day) for day in self._DAYS})

        # Fill in missing values in the dataframe
        new_index = list(range(0, 23+1))
        return matrix.reindex(new_index, fill_value=0).fillna(0)
    
    def _military_to_standard(self, hour: int) -> str:
        """Converts military hours (24 hours) to standard hours (am/pm)."""

        if not (1 <= hour <= 24):
            raise ValueError((
                f'{hour} is an incorrect military time hour. '
                'Valid range is between 1 and 24.'
            ))

        postfix = 'am'
        if hour == 12:
            postfix = 'pm'
        elif 12 < hour < 24:
            postfix = 'pm'
            hour -= 12
        elif hour == 24:
            hour -= 12
        return f'{hour} {postfix}'
    
    def _rotate_text(self, i: int, angle: float, slice_degrees: float) -> float:
        """Rotates the hour labels to be facing radially perpendicular."""
        return angle - (2*i+1)*slice_degrees/2 - (i-1)*slice_degrees


class FrequencyBarChart:
    """Class to create a frequency bar chart."""

    _VALID_SPINES = ['top', 'bottom', 'left', 'right']
    _VALID_AXES = ['x', 'y']
    _VALID_TICKS = ['major', 'minor']

    def __init__(self,
            data: list[tuple[emojis.Emoji, int]],
            figsize: tuple[int, int]=(7, 7),
        ):
        """Initializes the FrequencyBarChart object."""
        
        # Store the specified argument values
        self._data = data
        self._figsize = figsize

        # Split the data
        self._labels = [d[0] for d in self._data]
        self._counts = [d[1] for d in self._data]

        # Create the axis and figure
        self.figure, self.axis = plt.subplots(figsize=self._figsize)

    def generate(self,
        bar_color: str='blue',
        grid_color: tuple[float, float, float, float]=(0, 0, 0, 1),
        x_tick_size: Union[int, float]=10,
        x_tick_color: str='black',
        y_tick_size: Union[int, float]=10,
        y_tick_color: str='black',
        invert_yaxis: bool=True,
        bar_alpha: float=0.75,
    ):
        """Generates the frequency bar chart."""

        # Plot the bar chart
        self.axis.barh(
            self._labels, self._counts,
            color=bar_color, edgecolor=bar_color, alpha=bar_alpha,
        )

        # Customize the x axis
        self.set_grid_color('x', 'major', color=grid_color)
        self.set_grid_visibility('x', 'minor', visible=False)
        self.set_tick_label_color('x', 'major', color=x_tick_color)
        self.set_tick_label_size('x', 'major', size=x_tick_size)
        # Customize the y axis
        self.set_grid_color('y', 'minor', color=grid_color)
        self.set_grid_visibility('y', 'major', visible=False)
        self.set_tick_label_color('y', 'major', color=y_tick_color)
        self.set_tick_label_size('y', 'major', size=y_tick_size)
        self.set_left_tick_visibility(False)
        self.invert_yaxis(invert_yaxis)
        y_ticks = self.axis.get_yticks()
        self.axis.set_yticks(self._move_ticks_around_bars(y_ticks), minor=True)
        # General customization
        self.set_tick_colors(['x', 'y'], ['major', 'minor'], color=grid_color)
        self.move_grid_below_plot(True)
        self.toggle_spines(['top', 'right', 'bottom'], visible=False)
        self.set_spine_color('left', color=grid_color)

    def invert_yaxis(self, invert: bool=True):
        """Invert the y-axis of the plot."""

        if invert:
            self.axis.invert_yaxis()

    def move_grid_below_plot(self, below: bool=True):
        """Moves the grid below the plot."""
        self.axis.set_axisbelow(below)

    def set_left_tick_visibility(self, show_ticks: bool=False):
        """Toggles visibility of ticks on the left side of the chart."""
        self.axis.tick_params(axis='y', which='major', left=show_ticks)

    def set_tick_colors(self, axes: str, which: str, color: str='black'):
        """Set the colors of the specified ticks."""

        # Sets default axes and converts to a list if necessary
        if axes is None:
            axes = self._VALID_AXES
        elif isinstance(axes, str):
            axes = [axes]
        # Sets default ticks and converts to a list if necessary
        if which is None:
            which = self._VALID_TICKS
        elif isinstance(which, str):
            which = [which]
        # Checks if the inputs are valid
        self._check_valid_axes(axes)
        self._check_valid_ticks(which)

        # Set the tick colors
        for axis in axes:
            for tick in which:
                self.axis.tick_params(axis=axis, which=tick, color=color)

    def set_tick_label_color(self,
            axes: str, which: str, color: str='black',
        ):
        """Set the colors of the specified tick labels."""

        # Sets default axes and converts to a list if necessary
        if axes is None:
            axes = self._VALID_AXES
        elif isinstance(axes, str):
            axes = [axes]
        # Sets default ticks and converts to a list if necessary
        if which is None:
            which = self._VALID_TICKS
        elif isinstance(which, str):
            which = [which]
        # Checks if the inputs are valid
        self._check_valid_axes(axes)
        self._check_valid_ticks(which)

        # Set the tick label colors
        for axis in axes:
            for tick in which:
                self.axis.tick_params(axis=axis, which=tick, labelcolor=color)

    def set_tick_label_size(self,
            axes: str, which: str, size: float=10,
        ):
        """Set the size of the specified tick labels."""

        # Sets default axes and converts to a list if necessary
        if axes is None:
            axes = self._VALID_AXES
        elif isinstance(axes, str):
            axes = [axes]
        # Sets default ticks and converts to a list if necessary
        if which is None:
            which = self._VALID_TICKS
        elif isinstance(which, str):
            which = [which]
        # Checks if the inputs are valid
        self._check_valid_axes(axes)
        self._check_valid_ticks(which)

        # Set the tick label sizes
        for axis in axes:
            for tick in which:
                self.axis.tick_params(axis=axis, which=tick, labelsize=size)

    def set_grid_color(self,
            axes: str,
            which: str,
            color: tuple[float, float, float, float]=(0, 0, 0, 1),
        ):
        """Set the color of the gridlines. Also makes the grids visible."""

        # Sets default axes and converts to a list if necessary
        if axes is None:
            axes = self._VALID_AXES
        elif isinstance(axes, str):
            axes = [axes]
        # Sets default ticks and converts to a list if necessary
        if which is None:
            which = self._VALID_TICKS
        elif isinstance(which, str):
            which = [which]
        # Checks if the inputs are valid
        self._check_valid_axes(axes)
        self._check_valid_ticks(which)

        # Set the grid color
        for axis in axes:
            for tick in which:
                self.axis.grid(
                    True, axis=axis, which=tick,
                    color=color[:3], alpha=color[3],
                )

    def set_grid_visibility(self, axes: str, which: str, visible: bool=True):
        """Set the visibility of the gridlines."""

        # Sets default axes and converts to a list if necessary
        if axes is None:
            axes = self._VALID_AXES
        elif isinstance(axes, str):
            axes = [axes]
        # Sets default ticks and converts to a list if necessary
        if which is None:
            which = self._VALID_TICKS
        elif isinstance(which, str):
            which = [which]
        # Checks if the inputs are valid
        self._check_valid_axes(axes)
        self._check_valid_ticks(which)

        # Set the grid visibility
        for axis in axes:
            for tick in which:
                self.axis.grid(visible, axis=axis, which=tick)

    def enable_spines(self, spines: Optional[Union[str, list[str]]]=None):
        """Enables all specified spines of the chart."""
        self.toggle_spines(spines, visible=True)

    def disable_spines(self, spines: Optional[Union[str, list[str]]]=None):
        """Disabes all specified spines of the chart."""
        self.toggle_spines(spines, visible=False)

    def toggle_spines(self,
            spines: Optional[Union[str, list[str]]]=None,
            visible: bool=False,
        ):
        """Sets the visibility of all specified spines of the chart."""
        
        # Sets default spines and converts to a list if necessary
        if spines is None:
            spines = self._VALID_SPINES
        elif isinstance(spines, str):
            spines = [spines]
        # Checks if the inputs are valid
        self._check_valid_spines(spines)

        # Set the spine visibilities
        for spine in spines:
            self.axis.spines[spine].set_visible(visible)

    def set_spine_color(self,
            spines: Optional[Union[str, list[str]]]=None,
            color: str='black',
        ):
        """Sets the color of all specified spines of the chart."""
        
        # Sets default spines and converts to a list if necessary
        if spines is None:
            spines = self._VALID_SPINES
        elif isinstance(spines, str):
            spines = [spines]
        # Checks if the inputs are valid
        self._check_valid_spines(spines)

        # Set the spine colors
        for spine in spines:
            self.axis.spines[spine].set_color(color)

    def save(self, *args, **kwargs):
        """Wrapper around plt.savefig()."""
        plt.savefig(*args, **kwargs)
    
    def show(self):
        """Wrapper around plt.show()."""
        plt.show()

    def _move_ticks_around_bars(self, ticks: list[int]) -> list[int]:
        """
        Takes a list of ticks that are placed at the center of bars and
        calculates a new list of ticks that are placed outside the bars.
        """
        ticks = [tick+0.5 for tick in ticks]
        return [ticks[0] - 1] + ticks

    def _check_valid_axes(self, axes: Optional[Union[str, list[str]]]):
        """Raises an error if the user-specified axes are not valid."""

        if any(axis not in self._VALID_AXES for axis in axes):
           raise ValueError((
            f'{axes} is not a valid value for axis. '
            f'Valid values are {self._VALID_AXES}'
        ))

    def _check_valid_ticks(self, ticks: Optional[Union[str, list[str]]]):
        """Raises an error if the user-specified ticks are not valid."""

        if any(tick not in self._VALID_TICKS for tick in ticks):
           raise ValueError((
            f'{ticks} is not a valid value for which. '
            f'Valid values are {self._VALID_TICKS}'
        ))

    def _check_valid_spines(self, spines: Optional[Union[str, list[str]]]):
        """Raises an error if the user-specified spines are not valid."""

        if any(spine not in self._VALID_SPINES for spine in spines):
           raise ValueError((
            f'{spines} is not a valid value for spines. '
            f'Valid values are {self._VALID_SPINES}'
        ))


class StackedFrequencyBarChart(FrequencyBarChart):
    """
    Class to create a stacked frequency bar chart that shows the difference
    between sent and received data.
    """

    _VALID_LEGEND_LOCATIONS = ['top', 'bottom']

    def __init__(self,
            data: list[tuple[emojis.Emoji, int, int, int]],
            figsize: tuple[int, int]=(7, 7),
        ):
        """Initializes the StackedFrequencyBarChart object."""
        
        # Store the specified argument values
        self._data = data
        self._figsize = figsize

        # Split the data
        self._labels = [d[0] for d in self._data]
        self._all = [d[1] for d in self._data]
        self._sent = [d[2] for d in self._data]
        self._received = [d[3] for d in self._data]

        # Create the axis and figure
        self.figure, self.axis = plt.subplots(figsize=self._figsize)

    def generate(self,
        figsize: tuple[int, int]=(7, 7),
        sent_label: str='Sent',
        sent_color: str='blue',
        received_label: str='Received',
        received_color: str='orange',
        grid_color: tuple[float, float, float, float]=(0, 0, 0, 1),
        x_tick_size: Union[int, float]=10,
        x_tick_color: str='black',
        y_tick_size: Union[int, float]=10,
        y_tick_color: str='black',
        invert_yaxis: bool=True,
        bar_alpha: float=0.75,
        legend: bool=True,
        legend_y_offset: float=0,
        legend_label_size: Union[int, float]=10,
        legend_label_color: str='black',
        legend_location: str='top',
    ):
        """Generates the stacked frequency bar chart."""

        # Verify that inputs are valid
        self._check_valid_legend(legend_location)

        # Plot the stacked bar chart
        stack_1 = self.axis.barh(
            self._labels, self._sent,
            color=sent_color, edgecolor=sent_color, alpha=bar_alpha,
        )
        stack_2 = self.axis.barh(
            self._labels, self._received, left=self._sent,
            color=received_color, edgecolor=received_color, alpha=bar_alpha,
        )

        # Customize the legend
        if legend:
            box = self.axis.get_position()
            if legend_location == 'top':
                box_y = box.y0
                anchor = (0.5, 1.15 + legend_y_offset)
            else:
                box_y = box.y0 + box.height * 0.1
                anchor = (0.5, -0.05 + legend_y_offset)
            self.axis.set_position([box.x0, box_y, box.width, box.height * 0.9])
            self.axis.legend(
                [stack_1, stack_2], [sent_label, received_label],
                loc="upper center", frameon=False, fancybox=False, shadow=False,
                ncol=2, handleheight=1, handlelength=1, bbox_to_anchor=anchor,
                labelcolor=legend_label_color, prop={'size': legend_label_size},
            )

        # Customize the x axis
        self.set_grid_color('x', 'major', color=grid_color)
        self.set_grid_visibility('x', 'minor', visible=False)
        self.set_tick_label_color('x', 'major', color=x_tick_color)
        self.set_tick_label_size('x', 'major', size=x_tick_size)
        # Customize the y axis
        self.set_grid_color('y', 'minor', color=grid_color)
        self.set_grid_visibility('y', 'major', visible=False)
        self.set_tick_label_color('y', 'major', color=y_tick_color)
        self.set_tick_label_size('y', 'major', size=y_tick_size)
        self.set_left_tick_visibility(False)
        self.invert_yaxis(invert_yaxis)
        y_ticks = self.axis.get_yticks()
        self.axis.set_yticks(self._move_ticks_around_bars(y_ticks), minor=True)
        # General customization
        self.set_tick_colors(['x', 'y'], ['major', 'minor'], color=grid_color)
        self.move_grid_below_plot(True)
        self.toggle_spines(['top', 'right', 'bottom'], visible=False)
        self.set_spine_color('left', color=grid_color)

    def _check_valid_legend(self, location: Optional[Union[str, list[str]]]):
        """Raises an error if the user-specified location is not valid."""

        if location not in self._VALID_LEGEND_LOCATIONS:
            raise ValueError((
                f'{location} is not a valid value for legend_location. '
                f'Valid values are: {self._VALID_LEGEND_LOCATIONS}'
            ))


class CalendarHeatmap:
    """Create a calendar heatmap similar to Github's contributions plot."""

    def __init__(self, data: pd.DataFrame, year: Optional[int]=None, **kwargs):
        """Initializes the CalendarHeatmap instance.
        
        For information on keyword arguments, please see the documentation
        for the calmap library.
        """

        # Store instance variables
        self._data = data
        
        # Group the data by date and get the frequency for each
        grouped = self._data['message'].groupby([self._data.index.date]).count()

        # Convert the grouped data into a series
        events = pd.Series(grouped)
        events.index = pd.to_datetime(events.index)

        # Create the calendar heatmaps
        if isinstance(year, int):
            calmap.yearplot(events, year=year, **kwargs)
        else:
            # If no year is specified, plot all years
            calmap.calendarplot(events, **kwargs)

    def save(self, *args, **kwargs):
        """Wrapper around plt.savefig()."""
        plt.savefig(*args, **kwargs)
    
    def show(self):
        """Wrapper around plt.show()."""
        plt.show()