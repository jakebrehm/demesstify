#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for parsing and analyzing an iMessage conversation.
"""


import csv
import re
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

import pandas as pd

from . import database as db
from .analysis import reactions
from .testing import messages


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


class Direction(Enum):
    """Enumeration for valid message sending directionality."""
    ALL = 'all'
    SENT = 'sent'
    RECEIVED = 'received'


class Source(Enum):
    """Enumeration for valid data sources."""
    RANDOM = 'Random'
    TANSEE = 'Tansee'
    IMESSAGE_CSV = 'iMessage CSV'
    IMESSAGE_DB = 'iMessage DB'


class Parser(ABC):
    """Parses the input messages and converts into a standardized form."""

    _LABELS = ['datetime', 'is_sender', 'message', 'reaction']

    def parse(self) -> pd.DataFrame:
        """Parses the input and outputs it in a standardized form."""

        # Perform necessary operations
        unclean_text = self.load()
        cleaned_text = self.clean(unclean_text)
        standardized = self.standardize(cleaned_text)

        # Return the fully parsed and standardized text
        return standardized

    @abstractmethod
    def get(self) -> pd.DataFrame:
        """Gets the standardized dataframe."""
        pass

    @abstractmethod
    def load(self) -> str:
        """Meant to load the data from the source."""
        pass

    @abstractmethod
    def clean(self, text: str) -> list[Any]:
        """Meant to clean the input text and separate into lines."""
        pass
    
    @abstractmethod
    def standardize(self, lines: list[Any]) -> pd.DataFrame:
        """Standardizes the given lines of text."""
        pass


class Tansee(Parser):
    """Parses a Tansee text file."""

    _BLOCK_EXPRESSION: str = r'^(From|Send To) (.*)\((.*)\) at (.*)$'
    _DATETIME_FORMAT: str = r'%b %d, %Y %H:%M:%S'

    def __init__(self, path: str):
        """Initializes the Tansee instance."""
        
        # Store instance variables
        self._path = path

        # Parse the input
        self._parsed = self.parse()
    
    def get(self) -> pd.DataFrame:
        """Gets the standardized dataframe."""
        return self._parsed

    def load(self) -> str:
        """Loads and returns the data from the source."""

        # Open and read the text file
        with open(self._path, 'r') as text_file:
            return text_file.read()
    
    def clean(self, text: str) -> list[Any]:
        """Cleans the input text and separates into lines."""

        # Remove URLs from the text - done first to be more efficient
        text = remove_urls(text)

        # Clean the rest of the text line-by-line
        cleaned = [clean_line(line) for line in text.splitlines()]

        # Return the cleaned text
        return cleaned
    
    def standardize(self, lines: list[Any]) -> pd.DataFrame:
        """Standardizes the given lines of text.
        
        Converts the given lines of (presumably cleaned) text into a 
        dataframe that follows a standardized format.
        """
        
        # Convert the given lines into message blocks
        blocks = to_blocks(lines, self._BLOCK_EXPRESSION, dead_lines=1)
        headers, messages = zip(*blocks)
        
        # Extract information from the headers of each block
        groups = [re.search(self._BLOCK_EXPRESSION, line) for line in headers]
        directions = [self._to_sender_bool(group.group(1)) for group in groups]
        datetimes = [self._to_datetime(group.group(4)) for group in groups]
        reacts = [reactions.Reactions.get_reaction(line) for line in messages]

        # Create the standardized dataframe and set the index and return
        data = zip(self._LABELS, (datetimes, directions, messages, reacts))
        return pd.DataFrame(dict(data)).set_index(['datetime'])
    
    def _to_datetime(self, text: str) -> datetime:
        """Converts a Tansee datetime string to a Python datetime object."""
        
        return datetime.strptime(text, self._DATETIME_FORMAT)
    
    def _to_sender_bool(self, text: str) -> bool:
        """Convert is_sender strings to boolean values."""

        return {
            'Send To': True,
            'From': False,
        }.get(text, None)


class Random(Tansee):
    """Parses a dummy text file.
    
    For kwarg information, see the generate_sample_text function of the
    demesstify.testing.messages module.
    """

    def __init__(self, **kwargs):
        """Initializes the Random instance."""

        # Store instance variables
        self._kwargs = kwargs
        
        # Parse the input
        self._parsed = self.parse()

    def load(self) -> str:
        """Generates dummy text and returns the data as a string."""
        return messages.generate_sample_text(**self._kwargs)


class iMessageCSV(Parser):
    """Parses an iMessage csv.
    
    Parses a csv file that was generated by querying the local iMessage
    database (chat.db).

    The csv file should only have three columns:
        date, is_from_me, text
    All of these columns come from the message table of the database.
    It is also assumed that there is a header in this csv file.
    """

    def __init__(self, path: str, delimiter: str=','):
        """Initializes the iMessageCSV instance."""

        # Store instance variables
        self._path = path
        self._delimiter = delimiter

        # Parse the input
        self._parsed = self.parse()

    def get(self) -> pd.DataFrame:
        """Gets the standardized dataframe."""
        return self._parsed

    def load(self) -> str:
        """Loads the csv file and returns the data as a string."""
        
        # Open and read the csv file
        with open(self._path, 'r') as csv_file:
            return csv_file.read()

    def clean(self, text: str) -> list[Any]:
        """Cleans the input csv text and separates into lines."""

        # Remove URLs from the text - done first to be more efficient
        text = remove_urls(text)

        # Split the text by line and create a csv reader object
        lines = text.splitlines()[1:] # ignore the header
        reader = csv.reader(lines, delimiter=self._delimiter)
        
        # Clean each row of the csv file
        cleaned = []
        for r, (datetime, is_sender, message) in enumerate(reader):
            datetime = convert_mactime_to_datetime(datetime)
            is_sender = self._to_sender_bool(is_sender)
            cleaned.append([datetime, is_sender, clean_line(message)])

        # Return the cleaned text
        return cleaned
    
    def standardize(self, lines: list[Any]) -> pd.DataFrame:
        """Standardizes the given lines of text."""
        
        # Extract information from the given sublists
        datetimes, directions, messages = zip(*lines)
        reacts = [reactions.Reactions.get_reaction(line) for line in messages]

        # Create the standardized dataframe and set the index and return
        data = zip(self._LABELS, (datetimes, directions, messages, reacts))
        return pd.DataFrame(dict(data)).set_index(['datetime'])
    
    def _to_sender_bool(self, text: str) -> bool:
        """Convert is_sender strings to boolean values.
        
        These strings should either be a 0 or a 1.
        """

        return bool(int(text))


class iMessageDB(iMessageCSV):
    """Parses results from a query to the local iMessage database."""

    def __init__(self,
        path: Optional[str]=None, handle_id: Optional[int]=None,
        phone: Optional[str]=None, email: Optional[str]=None,
    ):
        """Initializes the iMessageDB instance.
        
        If no path is provided, the database will be assumed to be at its
        default location.

        At least one of the following parameters must be specified:
            handle_id, phone, email
        If more than one of them is provided, only the first will be used
        (assuming the previously listed order).
        """

        # Check for valid arguments
        if all(parameter is None for parameter in [handle_id, phone, email]):
            raise ValueError(
                f"At least one of the following parameters must be specified: "
                f"handle_id, phone, email"
            )

        # Store instance variables
        self._path = path
        self._handle_id = handle_id
        self._phone = phone
        self._email = email

        # Delimiter is necessary for some of the parent's methods
        self._delimiter = ','

        # Parse the input
        self._parsed = self.parse()
    
    def load(self) -> str:
        """Loads the csv file and returns the data as a string."""

        # Query the database depending on what parameters were provided
        chatdb = db.chat.ChatDB(self._path)
        if self._handle_id:
            df = chatdb.get_from_handle_id(self._handle_id)
        elif self._phone:
            df = chatdb.get_from_phone(self._phone)
        elif self._email:
            df = chatdb.get_from_email(self._email)
        
        # Return the csv string
        return df.to_csv(index=False)


class Messages:
    """The main object to handle message data."""

    def __init__(self,
        path: Optional[str]=None,
        source: Union[str, Source]=Source.IMESSAGE_DB,
        **kwargs,
    ):
        """Initializes the Messages instance."""

        # Convert source to enumeration if necessary
        if isinstance(source, str):
            source = Source(source)
        
        # Store instance variables
        self._path = path
        self._source = source

        # Get the data from the appropriate parser
        if self._source == Source.RANDOM:
            parser = Random(**kwargs)
        elif self._source == Source.TANSEE:
            parser = Tansee(self._path)
        elif self._source == Source.IMESSAGE_CSV:
            parser = iMessageCSV(self._path)
        elif self._source == Source.IMESSAGE_DB:
            parser = iMessageDB(self._path, **kwargs)
        self._data = parser.get()

    @classmethod
    def from_random(cls, **kwargs) -> 'Messages':
        """Initializes a Messages object using randomly generated dummy text.
        
        For kwarg information, see the generate_sample_text function of the
        demesstify.testing.messages module.
        """
        return cls(source=Source.RANDOM, **kwargs)

    @classmethod
    def from_tansee(cls, path: str) -> 'Messages':
        """Initializes a Messages object using a Tansee text file."""
        return cls(path=path, source=Source.TANSEE)

    @classmethod
    def from_imessage_csv(cls, path: str) -> 'Messages':
        """Initializes a Messages object using an iMessage CSV file."""
        return cls(path=path, source=Source.IMESSAGE_CSV)

    @classmethod
    def from_imessage_db(cls, path: Optional[str]=None, **kwargs) -> 'Messages':
        """Initializes a Messages object using the local iMessage database."""
        return cls(path=path, source=Source.IMESSAGE_DB, **kwargs)

    def get(self, which: Union[str, Direction]=Direction.ALL) -> pd.DataFrame:
        """Gets the message dataframe."""

        # Convert directionality to enumeration if necessary
        if isinstance(which, str):
            which = Direction(which)

        # Determine which data to return and return
        if which == Direction.ALL:
            return self.get_all()
        elif which == Direction.SENT:
            return self.get_sent()
        elif which == Direction.RECEIVED:
            return self.get_received()
    
    def get_all(self):
        """Gets the unfiltered main dataframe."""
        return self._data
    
    def get_sent(self):
        """Gets the main dataframe filtered by sent messages."""
        return self._data[self._data['is_sender'] == 1]
    
    def get_received(self):
        """Gets the main dataframe filtered by received messages."""
        return self._data[self._data['is_sender'] == 0]

    def as_string(self, 
            which: Union[str, Direction]=Direction.ALL,
            include_reactions: bool=False,
        ) -> str:
        """Gets the message data as a string, separated by new lines."""
        
        # Get the appropriately filtered data
        data = self.get(which=which)

        # Remove reactions if specified
        if not include_reactions:
            data = self._remove_reactions(data)

        # Return the message string
        return '\n'.join(data['message'])

    def trim(self, start: str, end: str, replace: bool=True) -> pd.DataFrame:
        """
        Trims the data to messages sent between a specified time interval.
        
        The start and end arguments generally should follow one of the
        following previoulsly-tested formats:
            %Y-%m-%d %H:%M:%S
            %Y-%m-%d
        That said, other formats may work.
        """

        trimmed = self._data.loc[start:end]
        if replace:
            self._data = trimmed
        return trimmed

    def _remove_reactions(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filters out reactions from a message dataframe."""
        return data[data['reaction'].isnull()]