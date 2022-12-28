#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the emojis that appear in a
given message conversation.
"""


import collections
from typing import Union

import emoji
import pandas as pd


class Emoji:
    """Class that tracks and represents a generic Emoji.
    
    Properties:
        name:
            The name/representation of the emoji.
    """

    def __init__(self, emoji: str, data: pd.DataFrame):
        """Initializes the Emoji object."""

        # Store instance variables
        self._emoji = emoji
        self._data = data

    @property
    def name(self) -> str:
        """Gets the name/representation of the emoji."""
        return self._emoji

    def get_messages(self) -> pd.DataFrame:
        """Gets all messages that contain the emoji."""
        return self._data
    
    def get_count(self) -> int:
        """Gets the number of occurrences of the emoji."""

        return self._count_emojis(self._data)

    def _count_emojis(self, df: pd.DataFrame) -> int:
        """Counts the number of occurrences of the emoji in a dataframe."""

        return df['message'].str.count(self.name).sum()
    
    def __repr__(self) -> str:
        """Returns a representation of an instance of Emoji."""
        return f"{self.__class__.__name__}('{self.name}')"

    def __str__(self) -> str:
        """Returns a string representation of the emoji."""
        return self.name


class Emojis:
    """Collection of Emoji objects.
    
    Properties:
        uniques:
            List of unique emojis that were found in the messages.
        emojis:
            List of emoji objects.
    """

    def __init__(self, data: pd.DataFrame):
        """Initializes the Emojis object."""

        # Store instance variables
        self._data = data

        # Initialize calculated instance variables
        messages = '\n'.join(self._data['message'])
        self._unique_emojis = emoji.distinct_emoji_list(messages)
        self._emoji_objects = self._create_emoji_objects(self._unique_emojis)
        self._counts = self._count_emojis(self._emoji_objects)

    @property
    def uniques(self) -> list[str]:
        """Gets a list of unique emojis that were found in the messages."""
        return self.get_uniques()
    
    @property
    def emojis(self) -> list[Emoji]:
        """Gets a list of emoji objects."""
        return list(self._emoji_objects.values())

    @property
    def emoji_objects(self) -> dict[str, Emoji]:
        """Gets a dictionary of emoji objects."""
        return self._emoji_objects
    
    def get_emoji_object(self, emoji: str) -> Emoji:
        """Gets the associated emoji object for an emoji."""
        return self.emoji_objects[emoji]

    def get_uniques(self) -> list[str]:
        """Gets a list of unique emojis that were found in the messages."""
        return self._unique_emojis
    
    def get_count(self, emoji: str) -> int:
        """Gets the number of times the specified emoji appeared."""
        return self._counts[emoji]

    def get_counts(self) -> dict[str, int]:
        """Gets the dictionary of emojis and their counts."""
        return self._counts

    def get_most_frequent(self,
            n: int, return_objects: bool=False
        ) -> list[tuple[Union[str, Emoji], int]]:
        """Gets the n most frequent emojis as a list of tuples."""

        counter = collections.Counter(self.get_counts())
        most_common = counter.most_common(n)
        if return_objects:
            for e, (emoji, count) in enumerate(most_common):
                most_common[e] = (self.get_emoji_object(emoji), count)
        return most_common

    def _count_emojis(self, emoji_objects: dict[str, Emoji]):
        """Counts the number of occurences of each unique emoji."""

        counts = {}
        for emoji_name, emoji_object in emoji_objects.items():
            counts[emoji_name] = emoji_object.get_count()
        return counts

    def _create_emoji_objects(self, emojis: str) -> dict[str, Emoji]:
        """Gets a dictionary of emoji objects."""

        messages = self._data
        emoji_objects = {}
        for emoji in emojis:
            df = messages[messages['message'].str.contains(emoji)]
            emoji_object = Emoji(emoji, data=df)
            emoji_objects[emoji] = emoji_object
        return emoji_objects
    
    def __getitem__(self, emoji: str) -> Emoji:
        """Gets the emoji object with the specified name."""
        return self._emoji_objects[emoji]