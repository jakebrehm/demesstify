#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the reactions that occur in
a given message conversation.
"""


from datetime import datetime, timedelta

import pandas as pd


class Text:
    """Generates useful calculations about given message data."""

    def __init__(self, data: pd.DataFrame):
        """Initializes the Messages object with message data."""

        # Store instance variables
        self._data = data
    
    def get_total(self) -> float:
        """Calculates the total number of messages exchanged."""
        return len(self._data['message'])

    def get_average_length(self) -> float:
        """Calculates the average length of individual messages."""
        return self._data['message'].str.len().mean()
    
    def get_least_per_day(self) -> float:
        """Calculates the least number of texts exchanged in a day."""
        grouped = self._data['message'].groupby(self._data.index.date)
        return grouped.count().min()
    
    def get_most_per_day(self) -> float:
        """Calculates the greatest number of texts exchanged in a day."""
        grouped = self._data['message'].groupby(self._data.index.date)
        return grouped.count().max()
    
    def get_average_per_day(self) -> float:
        """Calculates the average number of texts exchanged in a day."""
        grouped = self._data['message'].groupby(self._data.index.date)
        return grouped.count().mean()
    
    def get_count_of_substring(self, substring: str) -> int:
        """Calculates the number of occurrences of a substring."""
        return self._data['message'].str.count(substring).sum()
    
    def get_days_since_first_message(self, ceiling: bool=True) -> int:
        """Calculates the number of days since the first message.
        
        By default, this method will round the number of days up by taking the
        ceiling of the Timedelta object. If this is not desired, set the 
        ceiling parameter to False.
        """
        
        # Get the datetimes of the first and last messages
        first = self._data.first_valid_index()
        last = self._data.last_valid_index()
        # Return the number of days between these two datetimes
        return (last - first).ceil('D').days if ceiling else (last - first).days
    
    def get_count_of_days_with_messages(self) -> int:
        """Calculates the number of days where messages were exchanged."""

        # The number of days with messages is total days minus days without
        total_days = self.get_days_since_first_message()
        days_without = self.get_count_of_days_without_messages()
        return (total_days - days_without)
    
    def get_count_of_days_without_messages(self) -> int:
        """Calculates the number of days where no messages were exchanged."""
        
        # Get the dates of the first and last messages
        first = self._data.first_valid_index().date()
        last = self._data.last_valid_index().date()
        # Find the missing dates by comparing time range to index
        dates_with_messages = self._data.index.date
        all_dates = pd.date_range(start=first, end=last)
        # Return the number of days where messages were not exchanged
        return len(all_dates.difference(dates_with_messages))
    
    def get_most_consecutive(self) -> int:
        """Calculates the most messages exchanged unidirectionally in a row.
        
        This method only works when the data includes all messages, i.e.
        is not filtered by directionality.
        """

        # Get a local reference to the data
        df = self._data
        # Shift the dataframe by one to see where directionality changes
        direction_change = df['is_sender'].ne(df['is_sender'].shift())
        # Cumulative sum splits into blocks because False evaluates to 0
        blocks = direction_change.cumsum()
        # Group each block and extract the desired columns
        grouped = df.groupby(blocks)['is_sender']
        # Get the counts of each group
        counts = grouped.transform('size')

        # Return the max count
        return max(counts)
    
    def get_datetime_of_longest_silence(self) -> datetime:
        """Calculates the datetime of the longest time between messages."""
        return self._data.index.to_series().diff().idxmax().to_pydatetime()

    def get_longest_silence(self) -> timedelta:
        """Calculates the longest time between messages."""
        return self._data.index.to_series().diff().max().to_pytimedelta()