#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Helper functions for cleaning data.
"""


import re
from datetime import datetime

from ..analysis import reactions


def remove_urls(line: str) -> str:
    """Removes URLs from a given string."""

    reacts = reactions.get_reaction_names()
    reactions_string = '|'.join(reacts)

    url_expression = (
        r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)"
        r"(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s("
        r")<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    )
    url_reaction_expression = fr"({reactions_string}) \"{url_expression}\""
    if re.match(url_reaction_expression, line):
        return line
    line = re.sub(url_expression, '', line)
    return line


def clean_line(line: str) -> str:
    """Performs some cleaning operations on a string/line."""

    line = line.replace('￼', '')    # Remove empty space
    line = line.replace('“', '"')   # Replace quotes
    line = line.replace('”', '"')   # Replace quotes
    line = line.replace('’', "'")   # Replace quotes
    line = line.replace('�', '')    # Remove iMessage games
    line = line.replace('…', '...') # Replace unicode ellipses
    line = line.strip()
    return line


def to_blocks(lines: list[str], regex: str, dead_lines: int=0):
    """Splits a list into sublists.
    
    Will split wherever an element matches the specified regex expression.

    dead_lines are the number of lines at the end of each sublist to toss away.
    """

    # Determine where each block starts and ends
    block_starts = [i for i, line in enumerate(lines) if re.match(regex, line)]
    block_ends = block_starts[1:] + [len(lines)]

    # Split into blocks and return
    return [lines[i:j-dead_lines] for i, j in zip(block_starts, block_ends)]


def convert_mactime_to_datetime(date: str) -> datetime:
    """Converts from Mac Absolute Time to a DateTime object.
    
    MacTime represents the number of nanoseconds since 01/01/2001
    instead of seconds since 01/01/1970 (which is typical practice).
    """

    # Convert to seconds and add 31 years
    converted = (int(date)/1e9) + 978307200
    return datetime.fromtimestamp(converted)