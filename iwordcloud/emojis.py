#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the emojis that appear in a
given iMessage conversation.
"""


import collections
from typing import List, Dict, Tuple, Union

import emoji
import pandas as pd


class Emoji:
    """
    Class that tracks and represents a generic Emoji.
    
    Properties:
        name:
            The name/representation of the emoji.
    """

    def __init__(self, emoji: str, messages: pd.DataFrame):
        """Inits the Emoji object."""

        self._emoji = emoji
        self._messages = messages

    @property
    def name(self) -> str:
        """Returns the name/representation of the emoji."""
        return self._emoji

    def get_all_messages(self) -> pd.DataFrame:
        """Gets all messages that contain the emoji."""
        return self._messages
    
    def get_sent_messages(self) -> pd.DataFrame:
        """Gets all messages from the sender that contain the emoji."""

        messages = self.get_all_messages()
        return messages[messages['is_sender'] == 1]
    
    def get_received_messages(self) -> pd.DataFrame:
        """Gets all messages from the receiver that contain the emoji."""

        messages = self.get_all_messages()
        return messages[messages['is_sender'] == 0]
    
    def get_count(self, which: str='all') -> int:
        """Gets the number of occurrences of the emoji.
        
        Kwargs:
            which:
                Whether to get the count of all messages, or only messages
                from either the sender or the receiver. Possible values are
                'all' (default), 'sent', 'received'.
        """

        if which == 'all':
            return self.get_all_count()
        elif which == 'sent':
            return self.get_sent_count()
        elif which == 'received':
            return self.get_received_count()
        else:
            raise ValueError(f"{which} is not a valid value for 'which'.")

    def get_all_count(self) -> int:
        """Gets the number of occurrences of the emoji across all messages."""

        return self._count_emojis(self._messages)
    
    def get_sent_count(self) -> int:
        """
        Gets the number of occurrences of the emoji in the sender's messages.
        """

        return self._count_emojis(self.get_sent_messages())
    
    def get_received_count(self) -> int:
        """
        Gets the number of occurrences of the emoji in the receiver's messages.
        """

        return self._count_emojis(self.get_received_messages())
    
    def _count_emojis(self, df: pd.DataFrame) -> int:
        """Counts the number of occurrences of the emoji in a dataframe."""

        return df['message'].str.count(self.name).sum()

    def __str__(self) -> str:
        """Returns a string representation of the emoji."""
        return self.name
    
    def __repr__(self) -> str:
        """Returns a printable string representation of an instance of Emoji."""
        return f'{self.__class__.__name__}({self.name})'


class Emojis:
    """Collection of Emoji objects.
    
    Properties:
        uniques:
            List of unique emojis that were found in the messages.
        emojis:
            List of emoji objects.
    """

    def __init__(self, imessages: 'parser.iMessages'):
        """"""

        self._imessages = imessages

        messages = self._imessages.get_all()
        self._unique_emojis = emoji.distinct_emoji_list(messages)
        self._emoji_objects = self._create_emoji_objects(self._unique_emojis)
        self._counts = self._count_emojis(self._emoji_objects)

    @property
    def uniques(self) -> List[str]:
        """Returns a list of unique emojis that were found in the messages."""
        return self.get_uniques()
    
    @property
    def emojis(self) -> List[Emoji]:
        """Returns a list of emoji objects."""
        return list(self._emoji_objects.values())

    @property
    def emoji_objects(self) -> Dict[str, Emoji]:
        """Returns a dictionary of emoji objects."""
        return self._emoji_objects
    
    def get_emoji_object(self, emoji: str) -> Emoji:
        """Returns the associated emoji object for an emoji."""
        return self.emoji_objects[emoji]

    def get_uniques(self) -> List[str]:
        """Returns a list of unique emojis that were found in the messages."""
        return self._unique_emojis
    
    def get_count(self, emoji: str) -> int:
        """Returns the number of times the specified emoji appeared."""
        return self._counts[emoji]

    def get_counts(self) -> Dict[str, int]:
        """Returns the dictionary of emojis and their counts."""
        return self._counts

    def get_most_frequent(self,
            n: int, return_objects: bool=False
        ) -> List[Tuple[Union[str, Emoji], int]]:
        """Returns the n most frequent emojis as a list of tuples."""

        counter = collections.Counter(self.get_counts())
        most_common = counter.most_common(n)
        if return_objects:
            for e, (emoji, count) in enumerate(most_common):
                most_common[e] = (self.get_emoji_object(emoji), count)
        return most_common

    def _count_emojis(self, emoji_objects: Dict[str, Emoji]):
        """Counts the number of occurences of each unique emoji."""

        counts = {}
        for emoji_name, emoji_object in emoji_objects.items():
            counts[emoji_name] = emoji_object.get_count()
        return counts

    def _create_emoji_objects(self, emojis: str) -> Dict[str, Emoji]:
        """Returns a dictionary of emoji objects."""

        messages = self._imessages.data
        emoji_objects = {}
        for emoji in emojis:
            df = messages[messages['message'].str.contains(emoji)]
            emoji_object = Emoji(emoji, messages=df)
            emoji_objects[emoji] = emoji_object
        return emoji_objects
    
    def __getitem__(self, emoji: str) -> Emoji:
        """Returns the emoji object with the specified name."""
        return self._emoji_objects[emoji]