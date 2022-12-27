#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the reactions that occur in
a given message conversation.
"""


import pandas as pd


class Text:
    """Generates uses calculations about given message data."""

    def __init__(self, data: pd.DataFrame):
        """Inits the Messages object with message data."""

        self._data = data
    
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
