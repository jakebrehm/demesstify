#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for creating a WordCloud from a message conversation,
as well as functionality for further analyzing of the messages.
"""


import collections
import random
from typing import Any, Callable, Optional, Union

import numpy as np
from PIL import Image
from wordcloud import STOPWORDS, ImageColorGenerator, WordCloud

from .. import errors, parse


def requires_cloud(method: Callable) -> Callable:
    """
    Decorator that determines whether or not it is okay to run a method
    that typically requires first generating the WordCloud.
    """

    def inner(self, *args, **kwargs) -> Any:
        if not self.is_valid():
            raise errors.CloudNotGeneratedError()
        else:
            return method(self, *args, **kwargs)
    return inner


class Cloud(WordCloud):
    """Wrapper for the WordCloud object with added functionality.
    
    Can also store and analyze messages.

    Properties:
        words:
            Easy access to an object that provides message-analyzing
            functionality.
        mask:
            The custom mask that is used when generating the WordCloud.
    """

    # def __init__(self, messages: Optional[Union[str, parse.Messages]]=None):
    def __init__(self, messages: Optional[str]=None):
        """Initializes the Cloud instance, optionally with messages."""

        # Store the messages, or raise an exception if class is invalid
        if messages is None:
            self._data = None
        else:
            self.feed_messages(messages)

        # Init the parent class and initialize class variables
        super().__init__()
        self._words = Words()
        self._mask = None

        # Set default parameters
        self._set_defaults()
    
    @property
    def words(self) -> 'Words':
        """Return the words instance."""
        return self._words

    @property
    def mask(self) -> np.ndarray:
        """Returns the mask."""

        return self._mask

    @mask.setter
    def mask(self, value: Union[str, np.array]):
        """Sets the mask. Can be either a path to the file or a NumPy array."""

        if value is None:
            self._mask = None
        elif isinstance(value, str):
            self._mask = np.array(Image.open(value))
        elif isinstance(value, np.ndarray):
            self._mask = value
        else:
            raise ValueError(f'{type(value)} is not a valid type for a mask.')

    def feed_messages(self, messages: str):
        """Analyzes and stores the given messages as a class variable."""

        if isinstance(messages, str):
            self._data = messages
        else:
            raise ValueError(
                f"Type of messages argument {type(messages)} is invalid. "
                f"Must be of type str."    
            )

    def generate(self):
        """Generates the WordCloud and updates the Words instance."""

        super().generate(self._data)
        self._words.update(self)

    def save(self, path: str):
        """Wrapper around WordCloud's to_file method."""

        self.to_file(path)

    def add_stopwords(self, stopwords: Union[str, list[str]]):
        """Adds one or more words to the default set of stopwords."""

        if isinstance(stopwords, str):
            self.stopwords.add(stopwords)
        else:
            self.stopwords.update(stopwords)

    def _set_defaults(self):
        """Sets default WordCloud parameters."""

        self.stopwords = set(STOPWORDS)


class Words:
    """Helper class that provides access to word-related functions."""

    def __init__(self, cloud: Optional[Cloud]=None):
        """Initializes the Words object, with cloud data if specified."""

        if cloud is not None:
            self.update(cloud)
        else:
            self._cloud = None
            self._data = None
            self._frequencies = None

    def is_valid(self) -> bool:
        """
        Determines if it is viable to perform certain methods that require
        the WordCloud to be generated.
        
        Essentially checks if a Cloud object has been fed to the
        instance of Words.
        """

        attributes = [self._cloud]
        return all(attribute is not None for attribute in attributes)

    def update(self, cloud: Cloud):
        """Updates the cloud reference as well as other variables."""

        self._cloud = cloud
        self._data = self._cloud._data
        self._frequencies = self._cloud.process_text(self._data)

    @requires_cloud
    def get_counts(self) -> dict[str, int]:
        """Returns a dictionary with frequencies for each token."""

        return self._frequencies

    @requires_cloud
    def get_most_frequent(self, n: int) -> list[tuple[str, int]]:
        """Returns the n most frequent tokens as a list of tuples."""

        counter = collections.Counter(self.get_counts())
        return counter.most_common(n)