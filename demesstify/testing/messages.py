#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for creating sample message text files.
"""


import random
from datetime import datetime
from typing import Union, Optional

import lorem
import numpy as np
import pandas as pd

from . import settings as s


def generate_datetimes(
        start: Optional[datetime]=None,
        end: Optional[datetime]=None,
        periods: Optional[int]=None,
        uniform: Optional[bool]=None,
        as_string: bool=True,
    ) -> Union[pd.DatetimeIndex, list[str]]:
    """Generates a datetime between two datetime objects."""

    # Get default values from settings if necessary
    if start is None:
        start = s.START_DATETIME
    if end is None:
        end = s.END_DATETIME
    if periods is None:
        periods = s.TOTAL_MESSAGES
    if uniform is None:
        uniform = s.UNIFORMLY_DISTRIBUTED

    # Generate a range of datetimes from the start date to the end date
    if uniform:
        dates = pd.date_range(
            start,
            end,
            periods=periods,
            inclusive='both',
        ).to_pydatetime()
    else:
        dates = [random.random() * (end-start) + start for _ in range(periods)]
        dates = sorted(dates)
    
    # Return the list of datetimes, as a string if specified
    if as_string:
        dates = [date.strftime(s.DATE_FORMAT) for date in dates]
    return dates


def generate_block_sizes(n: int, total: str):
    """
    Essentially returns a random list of n positive integers summing to a
    specified total.
    """

    dividers = sorted(random.sample(range(1, total), n - 1))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]


def write_header(
        receiver_name: Optional[str]=None,
        receiver_phone: Optional[str]=None,
    ):
    """Writes the file header."""

    # Get default values from settings if necessary
    if receiver_name is None:
        receiver_name = s.RECEIVER_NAME
    if receiver_phone is None:
        receiver_phone = s.RECEIVER_PHONE
    
    # Writes the header of the dummy text, modeled after Tansee
    lines = []
    lines.append('=' * 70)
    lines.append(f"{' ' * 28}{receiver_name}({receiver_phone})")
    lines.append('=' * 70)
    lines.append('')
    return lines


def randomly_add_emoji(text: str, chance: Optional[float]=None):
    """Has a specified chance to add an emoji to the end of the given string."""

    # Get default values from settings if necessary
    if chance is None:
        chance = s.EMOJI_CHANCE

    # Determine whether or not to append an emoji
    if random.randint(1, 100)/100 > (1 - chance):
        text += f' {random.choice(s.EMOJIS)}'
    
    # Return the text
    return text


def write_message_block(
        from_sender: bool,
        name: str,
        phone: str,
        datetime: datetime,
        chance: Optional[float]=None,
    ):
    """Writes a block for each message."""
    
    # Get default values from settings if necessary
    if chance is None:
        chance = s.EMOJI_CHANCE
    
    # Make sure the chance argument is valid
    if not isinstance(chance, float) or not (0 <= chance <= 1):
        raise ValueError((f'chance should be a float between 0 and 1.'))

    # Construct the message block and return
    sender_template = f'Send To {name}({phone}) at {datetime}'
    receiver_template = f'From {name}({phone}) at {datetime}'
    preface = sender_template if from_sender else receiver_template
    message = lorem.sentence()
    message = randomly_add_emoji(lorem.sentence(), chance=chance)
    return [preface, message, '']


def generate_sample_text(
    output_path: Optional[str]=None,
    receiver_name: Optional[str]=None,
    receiver_phone: Optional[str]=None,
    start_date: Optional[datetime]=None,
    end_date: Optional[datetime]=None,
    total_messages: Optional[int]=None,
    uniform: Optional[bool]=None,
):
    """Generates a sample text file modeled after a Tansee text file."""

    # # Get default values from settings if necessary
    if receiver_name is None:
        receiver_name = s.RECEIVER_NAME
    if receiver_phone is None:
        receiver_phone = s.RECEIVER_PHONE
    if start_date is None:
        start_date = s.START_DATETIME
    if end_date is None:
        end_date = s.END_DATETIME
    if total_messages is None:
        total_messages = s.TOTAL_MESSAGES
    if uniform is None:
        uniform = s.UNIFORMLY_DISTRIBUTED

    # Generate equally spaced datetimes
    datetimes = generate_datetimes(
        start_date, end_date, total_messages, uniform=uniform,
    )
    # Generate messages block sizes
    block_sizes = generate_block_sizes(total_messages//2, total_messages)

    # Instantiate a list to store each line
    lines = []
    # Write a header
    header = write_header(receiver_name, receiver_phone)
    lines.extend(header)
    # Write blocks for each text message
    from_sender = True
    last_i = -1
    for block_size in block_sizes:
        for b_i in range(block_size):
            i = last_i + b_i + 1
            block = write_message_block(
                from_sender, receiver_name, receiver_phone, datetimes[i]
            )
            lines.extend(block)
        last_i = i
        from_sender = not from_sender
    messages = [f'{line}\n' for line in lines]

    # Write the sample text messages file if desired
    if output_path:
        with open(output_path, 'w') as text_file:
            # Write the lines list to the text file
            text_file.writelines(messages)
    
    # Return the messages string if desired
    return ''.join(messages)