#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for parsing and analyzing an iMessage conversation.
"""


import csv
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from . import database as db
from . import emojis, reactions
from .testing import messages


class TanseeTranscript:
    """Reads the text file and does some preliminary cleaning.
    
    Properties:
        path:
            The path of the text file.
        original:
            The original contents of the text file, split by line.
        cleaned:
            The cleaned contents of the text file, split by line.
    """

    def __init__(self, path: str):
        """Inits the TanseeTranscript object."""

        # Store instance variables
        self._path = path

        self._original = []
        self._cleaned = []
        with open(self._path, 'r') as text:
            transcript = self._remove_urls(text.read())
        for line in transcript.splitlines():
            cleaned_line = self._clean_line(line)
            self._cleaned.append(cleaned_line)
            self._original.append(line)

    @property
    def path(self) -> str:
        """Returns the path of the text file."""
        return self._path
    
    @property
    def original(self) -> List[str]:
        """Returns the original contents of the text file, split by line."""
        return self._original

    @property
    def cleaned(self) -> List[str]:
        """Returns the cleaned contents of the text file, split by line."""
        return self._cleaned

    def get(self, original: bool=False) -> List[str]:
        """Returns either the original or cleaned data."""
        return self.original if original else self.cleaned

    def _remove_urls(self, line: str) -> str:
        """Removes URLs from a given string."""

        reacts = reactions.Reactions._REACTIONS
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

    def _clean_line(self, line: str) -> str:
        """Performs some cleaning operations on a string/line."""

        line = line.replace('￼', '')    # Remove empty space
        line = line.replace('“', '"')   # Replace quotes
        line = line.replace('”', '"')   # Replace quotes
        line = line.replace('’', "'")   # Replace quotes
        line = line.replace('�', '')    # Remove iMessage games
        line = line.replace('…', '...') # Replace unicode ellipses
        # line = self._remove_urls(line)  # Remove links unless reacted to
        line = line.strip()
        return line


class iMessageCSVTranscript(TanseeTranscript):
    """"""

    def __init__(self, path: str, delimiter: str=',', header: bool=True):
        """Inits the iMessageCSVTranscript instance."""

        # Store instance variables
        self._path = path
        self._delimiter = delimiter
        self._header = header

        self._original = []
        self._cleaned = []

        with open(self._path, 'r') as csv_file:
            transcript = csv_file.read()
        transcript = self._remove_urls(transcript)

        reader = csv.reader(transcript.splitlines(), delimiter=self._delimiter)
        for r, row in enumerate(reader):
            joined_line = self._delimiter.join(row)
            if self._header and (r == 0):
                self._original.append(joined_line)
                continue
            self._original.append(joined_line)
            self._cleaned.append(row)

        # Convert the cleaned lines to the standard readable format
        self._cleaned = self._convert_to_standard_format(self._cleaned)

    def _convert_mactime_to_datetime(self, date: str) -> datetime:
        """Converts from Mac Absolute Time to a DateTime object.
        
        MacTime represents the number of nanoseconds since 01/01/2001
        instead of seconds since 01/01/1970 (which is typical practice).
        """

        # Convert to seconds and add 31 years
        converted = (int(date)/1e9) + 978307200
        return datetime.fromtimestamp(converted)

    def _convert_to_standard_format(self, messages: List[List]) -> List[str]:
        """"""

        transcript = []
        for date, is_sender, message in messages:
            direction = 'Send To' if int(is_sender) else 'From'
            name = 'Other Name'
            phone = 'Phone'
            dt_object = self._convert_mactime_to_datetime(date)
            formatted_date = datetime.strftime(dt_object, r'%b %d, %Y %H:%M:%S')
            header = f'{direction} {name}({phone}) at {formatted_date}'
            transcript.append(header)
            transcript.append(self._clean_line(message))
            transcript.append('')
        return transcript


class iMessageDBTranscript(iMessageCSVTranscript):
    """Pulls information from iMessage database to generate a transcript."""

    def __init__(self, 
            path: str, delimiter: str=',', header: bool=True, **kwargs
        ):
        """Inits the ChatDBTranscript instance."""
  
        # Handle kwargs
        valid_kwargs = ["handle_id", "phone", "email"]
        for kwarg in kwargs:
            if kwarg not in valid_kwargs:
                raise ValueError(
                    f"{kwarg} is an invalid keyword argument. "
                    f"Valid arguments are: {valid_kwargs}"
                )

        # Store instance variables
        self._path = path
        self._delimiter = delimiter
        self._header = header
        self._handle_id = kwargs.get("handle_id", None)
        self._phone = kwargs.get("phone", None)
        self._email = kwargs.get("email", None)

        self._original = []
        self._cleaned = []

        chatdb = db.chat.ChatDB(self._path)
        if self._handle_id:
            df = chatdb.get_from_handle_id(self._handle_id)
        elif self._phone:
            df = chatdb.get_from_phone(self._phone)
        elif self._email:
            df = chatdb.get_from_email(self._email)
        transcript = df.to_csv(index=False)
        transcript = self._remove_urls(transcript)

        reader = csv.reader(transcript.splitlines(), delimiter=self._delimiter)
        for r, row in enumerate(reader):
            joined_line = self._delimiter.join(row)
            if self._header and (r == 0):
                self._original.append(joined_line)
                continue
            self._original.append(joined_line)
            self._cleaned.append(row)

        # Convert the cleaned lines to the standard readable format
        self._cleaned = self._convert_to_standard_format(self._cleaned)      


class GeneratedSampleText(TanseeTranscript):
    """Generates a transcript from placeholder text."""

    def __init__(self, **kwargs):
        """Inits the GeneratedSampleText instance."""

        text = messages.generate_sample_text(**kwargs)

        self._original = []
        self._cleaned = []
        transcript = self._remove_urls(text)
        for line in transcript.splitlines():
            cleaned_line = self._clean_line(line)
            self._cleaned.append(cleaned_line)
            self._original.append(line)


class DataParser:
    """Parses and cleans a text file containing text messages."""

    _LABELS = ['datetime', 'is_sender', 'message', 'reaction']
    _BLOCK_EXPRESSION = r'^(From|Send To) (.*)\((.*)\) at (.*)$'

    def __init__(self,
        path: str=None,
        source: str='iMessage DB',
        _random_kwargs: Dict[str, Any]=None,
    ):
        """Inits the DataParser object."""

        if (path is None) and (source not in ['Random', 'iMessage DB']):
            raise ValueError((
                'A path is required for any source that is not a randomly '
                'generated sample.'
            ))

        self._path = path
        self._source = source

        if source == 'Tansee':
            self._transcript = TanseeTranscript(self._path)
        elif source == 'Random':
            self._transcript = GeneratedSampleText(**_random_kwargs)
        elif source == 'iMessage CSV':
            self._transcript = iMessageCSVTranscript(self._path)
        elif source == 'iMessage DB':
            self._transcript = iMessageDBTranscript(
                path=self._path, **_random_kwargs,
            )
        else:
            raise ValueError(f"'{source}' is not a valid message source.")
        self._data = self._parse(self._transcript)
    
    def get(self) -> pd.DataFrame:
        """Returns the message dataframe."""
        return self._data

    def _parse(self, transcript: TanseeTranscript) -> pd.DataFrame:
        """Parses and cleans the transcript into a dataframe."""

        all_texts = []
        record = False
        previous_message = None
        for line in transcript.get():
            if not self._is_valid_message(line):
                record = False
                continue
            if record:
                reaction, cleaned = reactions.Reactions.is_reaction(line)
                is_sender = (direction != 'From')
                if cleaned != previous_message:
                    all_texts.append((dt_object, is_sender, cleaned, reaction))
                    previous_message = cleaned
                record = False
                continue
            if re.match(self._BLOCK_EXPRESSION, line):
                result = re.search(self._BLOCK_EXPRESSION, line)
                direction = result.group(1)
                name = result.group(2)
                phone = result.group(3)
                dt_string = result.group(4)
                dt_object = datetime.strptime(dt_string, r'%b %d, %Y %H:%M:%S')
                record = True
        return self._create_dataframe(all_texts)

    def _is_valid_message(self, line: str) -> bool:
        """Determines if a line is valid for recording."""

        return line.strip() # Essentially checks if the line is empty

    def _create_dataframe(self, data: List[str]) -> pd.DataFrame:
        """Creates a dataframe from a list of strings/lines."""
        
        df = pd.DataFrame(data, columns=self._LABELS)
        return df.set_index(df['datetime'])


class Messages:
    """Helper class that provides access to message analysis functions."""

    def __init__(self, data: pd.DataFrame):
        """Inits the Messages object with message data."""

        self._data = data
    
    def get(self) -> pd.DataFrame:
        """Returns the message data."""
        return self._data
    
    def get_total(self) -> float:
        """Returns the total number of messages exchanged."""
        return len(self._data['message'])

    def get_average_length(self) -> float:
        """Returns the average length of individual messages."""
        return self._data['message'].str.len().mean()
    
    def get_least_per_day(self) -> float:
        """Returns the least number of texts exchanged in a day."""
        grouped = self._data['message'].groupby(self._data.index.date)
        return grouped.count().min()
    
    def get_most_per_day(self) -> float:
        """Returns the greatest number of texts exchanged in a day."""
        grouped = self._data['message'].groupby(self._data.index.date)
        return grouped.count().max()
    
    def get_average_per_day(self) -> float:
        """Returns the average number of texts exchanged in a day."""
        grouped = self._data['message'].groupby(self._data.index.date)
        return grouped.count().mean()
    
    def get_count_of_word(self, word: str) -> int:
        """Returns the number of occurrences of a word.
        
        Note that this function also matches substrings (parts of a word).
        """
        return self._data['message'].str.count(word).sum()


class iMessages:
    """The main object for analyzing iMessage conversations.
    
    Properties:
        data:
            The main dataframe.
        all:
            A Messages object containing data for all messages.
        sent:
            A Messages object containing data for sent messages.
        received:
            A Messages object containing data for received messages.
        reactions:
            The Reactions object for convenient access to its properties and
            methods.
        emojis:
            The Emojis object for convenient access to its properties and
            methods.
    """

    def __init__(self,
        path: Optional[str]=None,
        source='iMessage DB',
        _random_kwargs: Optional[Dict[str, Any]]=None,
    ):
        """Inits the iMessages object."""

        # Store instance variables
        self._path = path
        self._source = source

        parser = DataParser(
            self._path,
            source=self._source,
            _random_kwargs=_random_kwargs,
        )
        self._data = parser.get()

        self._split_data()

        self._reactions = reactions.Reactions(messages=self._data)
        self._emojis = emojis.Emojis(imessages=self)

    @property
    def data(self) -> pd.DataFrame:
        """Returns the main dataframe."""
        return self._data

    @data.setter
    def data(self, new_data):
        """Set the main dataframes."""
        self._data = new_data
        self._split_data()

    @property
    def all(self) -> Messages:
        """Returns the main Messages object."""
        return self._all

    @property
    def sent(self) -> Messages:
        """Returns the sent Messages object."""
        return self._sent
    
    @property
    def received(self) -> Messages:
        """Returns the received Messages object."""
        return self._received

    @property
    def reactions(self) -> reactions.Reactions:
        """
        Returns the Reactions object for convenient access to its
        properties and methods.
        """
        return self._reactions

    @property
    def emojis(self) -> emojis.Emojis:
        """
        Returns the Emojis object for convenient access to its
        properties and methods.
        """

        return self._emojis

    def get_all(self, include_reactions: bool=False, as_df: bool=False) -> str:
        """Returns all messages with or without reactions messages."""

        if include_reactions:
            data = self.data['message']
        else:
            data = self._remove_reactions(self.data)['message']
        return data if as_df else '\n'.join(data)
    
    def get_sent(self, include_reactions: bool=False, as_df: bool=False) -> str:
        """Returns all sent messages with or without reactions messages."""

        if include_reactions:
            data = self._filter_sent()['message']
        else:
            data = self._remove_reactions(self._filter_sent())['message']
        return data if as_df else '\n'.join(data)
    
    def get_received(self, include_reactions: bool=False, as_df: bool=False) -> str:
        """Returns all received messages with or without reactions messages."""

        if include_reactions:
            data = self._filter_received()['message']
        else:
            data = self._remove_reactions(self._filter_received())['message']
        return data if as_df else '\n'.join(data)

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
            self.data = trimmed
        return trimmed

    def save_all(self, path: str):
        """Saves all messages to a text file."""

        messages = self.get_all()
        with open(path, 'w') as text:
            text.write(messages)

    def _split_data(self):
        """Splits data into three message groups: all, sent, and received."""

        self._all = Messages(self.data)
        self._sent = Messages(self._filter_sent())
        self._received = Messages(self._filter_received())

    def _filter_sent(self) -> pd.DataFrame:
        """Returns the main dataframe filtered by sent messages."""
        return self._data[self._data['is_sender'] == 1]
    
    def _filter_received(self) -> pd.DataFrame:
        """Returns the main dataframe filtered by received messages."""
        return self._data[self._data['is_sender'] == 0]

    def _remove_reactions(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filters out reactions from a message dataframe."""
        return data[data['reaction'].isnull()]

    @classmethod
    def from_tansee_text_file(cls, path: str) -> 'iMessages':
        """Inits an iMessages object using a Tansee text file."""
        return cls(path=path, source='Tansee')

    @classmethod
    def from_random(cls, **kwargs) -> 'iMessages':
        """Inits an iMessages object using randomly generated messages."""
        return cls(source='Random', _random_kwargs=kwargs)

    @classmethod
    def from_imessage_csv(cls, path: str) -> 'iMessages':
        """Inits an iMessages object using an iMessage CSV file."""
        return cls(path=path, source='iMessage CSV')

    @classmethod
    def from_imessage_db(cls, path: Optional[str]=None, **kwargs) -> 'iMessages':
        """Inits an iMessages object using an iMessage CSV file."""
        return cls(path=path, source='iMessage DB', _random_kwargs=kwargs)