import os
import random
from datetime import datetime
from typing import List, Union

import lorem
import numpy as np
import pandas as pd


# Get the path to the data directory
PARENT_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
DATA_DIRECTORY = os.path.join(PARENT_DIRECTORY, 'data')

# Get the path to import files in the data directory
OUTPUT_PATH = os.path.join(DATA_DIRECTORY, 'sample.txt')

# Specify the number of messages
TOTAL_MESSAGES = 100

# Specify the emojis to randomly interject
EMOJIS = ['😊', '😁', '😭', '😘', '😍', '❤️', '👍', '😂', '🤤']
EMOJI_CHANCE = 0.1

# Specify other variables
SENDER_NAME = 'Joe Smith'
RECEIVER_NAME = 'Jane Doe'
SENDER_PHONE =  14094378951
RECEIVER_PHONE = 15558675309
DATE_FORMAT = r'%b %-d, %Y %H:%M:%S'
START_DATE = datetime(2017, 11, 28, 23, 55, 59)
END_DATE = datetime(2017, 12, 25, 17, 11, 22)


def generate_datetimes(
        start: datetime, end: datetime, periods: int, as_string: bool=True,
    ) -> Union[pd.DatetimeIndex, List[str]]:
    """Generates a datetime between two datetime objects."""

    dates = pd.date_range(start, end, periods=periods, inclusive='both')
    if as_string:
        dates = [date.strftime(DATE_FORMAT) for date in dates]
    return dates


def generate_block_sizes(n: int, total: int):
    """
    Essentially returns a random list of n positive integers summing to a
    specified total.
    """

    dividers = sorted(random.sample(range(1, total), n - 1))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]


def write_header(receiver_name: str, receiver_phone: str):
    """Writes the file header."""

    lines = []
    lines.append('=' * 70)
    lines.append(f"{' ' * 28}{receiver_name}({receiver_phone})")
    lines.append('=' * 70)
    lines.append('')
    return lines


def randomly_add_emoji(text: str, chance: float=EMOJI_CHANCE):
    """Has a specified chance to add an emoji to the end of the given string."""

    # 
    if random.randint(1, 100)/100 > (1 - chance):
        text += f' {random.choice(EMOJIS)}'
    return text


def write_message_block(
        from_sender: bool, name: str, phone: str, datetime: datetime,
    ):
    """Writes a block for each message."""

    sender_template = f'Send To {name}({phone}) at {datetime}'
    receiver_template = f'From {name}({phone}) at {datetime}'
    preface = sender_template if from_sender else receiver_template
    message = lorem.sentence()
    message = randomly_add_emoji(lorem.sentence(), chance=EMOJI_CHANCE)
    return [preface, message, '']


if __name__ == '__main__':

    # Generate equally spaced datetimes
    datetimes = generate_datetimes(START_DATE, END_DATE, TOTAL_MESSAGES)
    # Generate messages block sizes
    block_sizes = generate_block_sizes(TOTAL_MESSAGES//2, TOTAL_MESSAGES)

    # Write the sample text messages file
    with open(OUTPUT_PATH, 'w') as text_file:
        # Instantiate a list to store each line
        lines = []
        # Create a header
        header = write_header(RECEIVER_NAME, RECEIVER_PHONE)
        lines.extend(header)
        # Create blocks for each text message
        from_sender = True
        for block_length, datetime in zip(block_sizes, datetimes):
            for _ in range(block_length):
                block = write_message_block(
                    from_sender, RECEIVER_NAME, RECEIVER_PHONE, datetime
                )
                lines.extend(block)
            from_sender = not from_sender
        # Write the lines list to the text file
        text_file.writelines([f'{line}\n' for line in lines])