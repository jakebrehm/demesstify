#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functions related to colors.
"""


import random


def random_color(
        word=None, font_size=None, position=None,  orientation=None,
        font_path=None, random_state=None,
    ):
    """Returns an HSL value for a completely random color."""

    h = int(360.0 * float(random.randint(0, 255)) / 255.0)
    s = int(100.0 * float(random.randint(0, 255)) / 255.0)
    l = int(100.0 * float(random.randint(0, 255)) / 255.0)

    return f"hsl({h}, {s}%, {l}%)"


def random_gray(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    """Randomly generates a gray HSL color value."""

    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def constant_hue(hue):
    """
    Returns a function that itself returns an HSL value for a color with a
    constant hue but with some variation in lightness.
    """

    def _constant_hue(
            word=None, font_size=None, position=None,  orientation=None,
            font_path=None, random_state=None,
        ):
        h = hue
        s = int(100.0 * 255.0 / 255.0)
        l = int(100.0 * float(random.randint(60, 120)) / 255.0)

        return f"hsl({h}, {s}%, {l}%)"

    return _constant_hue