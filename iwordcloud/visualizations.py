#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for visualizing iMessage messages.
"""


from typing import Tuple, Union, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import parser


class WeekdayRadialHeatmap:
    """Class to create a radial heatmap of text message frequency.
    
    The radial heatmap has 24 slices (1 for each hour of the day) and 7 layers
    (1 for each day of the week). Each cell of the heatmap is then colored
    according to the specified colormap, with color intensity determined by
    the frequency of text messages during that day and time.
    """

    _DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
             'Friday', 'Saturday']

    def __init__(self, imessages: parser.iMessages, whom: str='all'):
        """Inits the WeekdayRadialHeatmap object."""

        # Extract relevant data from iMessages object
        self._imessages = imessages
        if whom == 'all':
            self._data = self._imessages.all.get()
        elif whom == 'sender':
            self._data = self._imessages.sent.get()
        elif whom == 'recipient':
            self._data = self._imessages.received.get()
        else:
            raise ValueError(f"'{whom}' is not a valid value for 'whom'.")
        
        # Construct the frequency matrix
        self._matrix_df = self._construct_frequency_matrix(self._data)
        self._matrix = self._matrix_df.to_numpy()

    def generate(self,
            figsize: Tuple[int, int]=(7, 7),
            cmap: Union[str, mpl.colors.Colormap]='viridis',
            spine_color: str='black',
            grid_color: str='black',
            text_color: str='black',
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
                label.set_color(text_color)

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
                label.set_color(text_color)
        
        # Turn off tick labels because they were replaced with text annotations
        self.axis.set_xticklabels([])
        self.axis.set_yticklabels([])

        # Customize spines
        self.axis.spines['polar'].set_color(spine_color)
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
                    cbar_label, color=text_color, fontsize=font_size,
                )
            if cbar_title:
                self.colorbar.ax.set_title(
                    cbar_title, color=text_color, fontsize=font_size,
                )
            self.colorbar.ax.xaxis.set_tick_params(
                color=cbar_outline_color, labelcolor=text_color,
            )
            self.colorbar.ax.yaxis.set_tick_params(
                color=cbar_outline_color, labelcolor=text_color,
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
        Takes iMessages object data and converts it into a usable matrix form
        which contains text message frequency information for each hour of
        each day of the week.
        """

        # Group the data by weekday and then by hour, and count frequencies
        grouped = data['message'].groupby([data.index.day_name(),
                                           data['datetime'].dt.hour]).count()
        
        # Create a dataframe from the grouped data
        matrix = pd.DataFrame({day: grouped[day] for day in self._DAYS})

        # Fill in missing values in the dataframe
        new_index = list(range(matrix.index.min()+1, matrix.index.max()+2))
        return matrix.reindex(new_index, fill_value=0).fillna(0)
    
    def _military_to_standard(self, hour: int) -> str:
        """
        Converts a military hour (24 hours) to a standard hour (12 hour am/pm).
        """

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