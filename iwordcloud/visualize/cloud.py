#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for creating a WordCloud from an iMessage conversation,
as well as functionality for further analyzing of the messages.
"""


import collections
import random
from typing import Callable, List, Dict, Tuple, Set, Union

import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from .. import errors
from .. import parser


def requires_cloud(method):
    """
    Decorator that determines whether it is okay to run a method
    that typically requires first generating the WordCloud.
    """

    def inner(self, *args, **kwargs):
        if not self.is_valid():
            raise errors.CloudNotGeneratedError()
        else:
            return method(self, *args, **kwargs)
    return inner


class MessageCloud(WordCloud):
    """Wrapper for the WordCloud object with added functionality.
    
    Can also store and analyze messages.

    Properties:
        words:
            Easy access to an object that provides message-analyzing
            functionality.
        mask:
            The custom mask that is used when generating the WordCloud.
    """

    def __init__(self, messages: Union[str, parser.iMessages]=None):
        """Inits the MessageCloud instance, optionally with messages."""

        # Store the messages, or raise an exception is class is invalid
        if messages is None:
            self._messages = None
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

    def feed_messages(self, messages: Union[str, parser.iMessages]):
        """Analyzes and stores the given messages as a class variable."""

        if isinstance(messages, str):
            with open(messages, 'r') as text:
                self._messages = text.read()
        elif isinstance(messages, parser.iMessages):
            self._messages = messages.get_all()
        else:
            raise errors.MessageArgumentError(type(messages))

    def generate(self):
        """Generates the WordCloud and updates the Words instance."""

        super().generate(self._messages)
        self._words.update(self)

    def save(self, path: str):
        """Wrapper around WordCloud's to_file method."""

        self.to_file(path)

    def add_stopwords(self, stopwords: Union[str, List[str]]):
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

    def __init__(self, messagecloud: MessageCloud=None):
        """Inits the Words object, with cloud data if specified."""

        if messagecloud is not None:
            self.update(messagecloud)
        else:
            self._cloud = None
            self._messages = None
            self._frequencies = None

    def is_valid(self) -> bool:
        """
        Determines if it is viable to perform certain methods that require
        the WordCloud to be generated.
        
        Essentially checks if a MessageCloud object has been fed to the
        instance of Words.
        """

        attributes = [self._cloud]
        return all(attribute is not None for attribute in attributes)

    def update(self, messagecloud: MessageCloud):
        """Updates the cloud reference as well as other variables."""

        self._cloud = messagecloud
        self._messages = self._cloud._messages
        self._frequencies = self._cloud.process_text(self._messages)

    @requires_cloud
    def get_counts(self) -> Dict[str, int]:
        """Returns a dictionary with frequencies for each token."""

        return self._frequencies

    @requires_cloud
    def get_most_frequent(self, n: int) -> List[Tuple[str, int]]:
        """Returns the n most frequent tokens as a list of tuples."""

        counter = collections.Counter(self.get_counts())
        return counter.most_common(n)