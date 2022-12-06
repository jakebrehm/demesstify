#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for creating sample message text files.
"""


import random
from datetime import datetime
from typing import List, Union, Optional

import lorem
import numpy as np
import pandas as pd

from . import settings as s


def generate_datetimes(
        start: Optional[datetime]=None,
        end: Optional[datetime]=None,
        periods: Optional[int]=None,
        as_string: bool=True,
    ) -> Union[pd.DatetimeIndex, List[str]]:
    """Generates a datetime between two datetime objects."""

    if start is None:
        end = s.START_DATETIME
    if end is None:
        end = s.END_DATETIME
    if periods is None:
        periods = s.TOTAL_MESSAGES

    dates = pd.date_range(
        start,
        end,
        periods=periods,
        inclusive='both',
    ).to_pydatetime()
    
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

    # Set variables if not specified
    if receiver_name is None:
        receiver_name = s.RECEIVER_NAME
    if receiver_phone is None:
        receiver_phone = s.RECEIVER_PHONE
    
    lines = []
    lines.append('=' * 70)
    lines.append(f"{' ' * 28}{receiver_name}({receiver_phone})")
    lines.append('=' * 70)
    lines.append('')
    return lines


def randomly_add_emoji(text: str, chance: Optional[float]=None):
    """Has a specified chance to add an emoji to the end of the given string."""

    # Set chance if it is not specified
    if chance is None:
        chance = s.EMOJI_CHANCE

    # 
    if random.randint(1, 100)/100 > (1 - chance):
        text += f' {random.choice(s.EMOJIS)}'
    return text


def write_message_block(
        from_sender: bool,
        name: str,
        phone: str,
        datetime: datetime,
        chance: Optional[float]=None,
    ):
    """Writes a block for each message."""
    
    # Set chance if it is not specified
    if chance is None:
        chance = s.EMOJI_CHANCE
    
    # Make sure the chance argument is valid
    if not isinstance(chance, float) or not (0 <= chance <= 1):
        raise ValueError((f'chance should be a float between 0 and 1.'))

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
):
    """Generates a sample text file."""

    if receiver_name is None:
        receiver_name = s.RECEIVER_NAME
    if receiver_phone is None:
        receiver_phone = s.RECEIVER_PHONE
    if start_date is None:
        end_date = s.START_DATETIME
    if end_date is None:
        end_date = s.END_DATETIME
    if total_messages is None:
        total_messages = s.TOTAL_MESSAGES

    # Generate equally spaced datetimes
    datetimes = generate_datetimes(start_date, end_date, total_messages)
    # Generate messages block sizes
    block_sizes = generate_block_sizes(total_messages//2, total_messages)

    # Instantiate a list to store each line
    lines = []
    # Create a header
    header = write_header(receiver_name, receiver_phone)
    lines.extend(header)
    # Create blocks for each text message
    from_sender = True
    for block_length, datetime in zip(block_sizes, datetimes):
        for _ in range(block_length):
            block = write_message_block(
                from_sender, receiver_name, receiver_phone, datetime
            )
            lines.extend(block)
        from_sender = not from_sender
    messages = [f'{line}\n' for line in lines]

    # Write the sample text messages file if desired
    if output_path:
        with open(output_path, 'w') as text_file:
            # Write the lines list to the text file
            text_file.writelines(messages)
    
    # Return the messages string if desired
    return ''.join(messages)