#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the attachments that
were exchanged in a given message conversation.
"""


from datetime import datetime, timedelta
from typing import Optional, Union

import pandas as pd

from .. import database as db
from .. import clean
from ..parse import Direction


class Attachment:
    """Analyzes attachments data."""

    def __init__(self, data: pd.DataFrame):
        """Initializes the Attachment object."""

        # Store instance variables
        self._data = data

    def get_total(self) -> int:
        """Calculates the total number of attachments exchanged."""
        return len(self._data)
    
    def get_average_per_day(self) -> float:
        """Calculates the average number of attachments exchanged in a day."""
        grouped = self._data['message'].groupby(self._data.index.date)
        return grouped.count().mean()

    def get_least_per_day(self) -> float:
        """Calculates the least number of attachments in a day."""
        grouped = self._data['filename'].groupby(self._data.index.date)
        return grouped.count().min()
    
    def get_most_per_day(self) -> float:
        """Calculates the greatest number of attachments in a day."""
        grouped = self._data['filename'].groupby(self._data.index.date)
        return grouped.count().max()

    def get_days_since_first_attachment(self, ceiling: bool=True) -> int:
        """Calculates the number of days since the first attachment.
        
        By default, this method will round the number of days up by taking the
        ceiling of the Timedelta object. If this is not desired, set the 
        ceiling parameter to False.
        """
        
        # Get the datetimes of the first and last attachments
        first = self._data.first_valid_index()
        last = self._data.last_valid_index()
        # Return the number of days between these two datetimes
        return (last - first).ceil('D').days if ceiling else (last - first).days

    def get_count_of_days_with_attachments(self) -> int:
        """Calculates the number of days where attachments were exchanged."""

        # The number of days with attachments is total days minus days without
        total_days = self.get_days_since_first_attachment()
        days_without = self.get_count_of_days_without_attachments()
        return (total_days - days_without)
    
    def get_count_of_days_without_attachments(self) -> int:
        """Calculates the number of days where no attachments were exchanged."""
        
        # Get the dates of the first and last attachments
        first = self._data.first_valid_index().date()
        last = self._data.last_valid_index().date()
        # Find the missing dates by comparing time range to index
        dates_with_attachments = self._data.index.date
        all_dates = pd.date_range(start=first, end=last)
        # Return the number of days where attachments were not exchanged
        return len(all_dates.difference(dates_with_attachments))

    def get_datetime_of_longest_silence(self) -> datetime:
        """Calculates the datetime of the longest time between attachments."""
        return self._data.index.to_series().diff().idxmax().to_pydatetime()

    def get_longest_silence(self) -> timedelta:
        """Calculates the longest time between attachments."""
        return self._data.index.to_series().diff().max().to_pytimedelta()

    def get_attachments_with_filetype(self, extension: str) -> pd.DataFrame:
        """Gets the attachments dataframe filtered by the specified filetype."""
        
        # Add a period if necessary
        if extension[0] != '.':
            extension = f".{extension}"

        # Count the number of attachments that have that extension
        return self._data[self._data['transfer_name'].str.endswith(extension)]

    def get_count_of_filetype(self, extension: str) -> int:
        """Calculates the number of attachments with the specified filetype."""
        return len(self.get_attachments_with_filetype(extension))


class Attachments:
    """Tracks and analyzes attachments from the local iMessage database.
    
    Properties:
        path:
            The filepath to the local iMessage database.
    """

    def __init__(self,
            path: Optional[str]=None, handle_id: Optional[int]=None,
            phone: Optional[str]=None, email: Optional[str]=None,
        ):
        """Initializes the Attachments object.
        
        If no path is provided, the database will be assumed to be at its
        default location.

        At least one of the following parameters can be specified:
            handle_id, phone, email
        If more than one of them is provided, only the first will be used
        (assuming the previously listed order).

        However, if none of the parameters are specified, the entire 
        database will be read.
        """

        # Store instance variables
        self._path = path
        self._handle_id = handle_id
        self._phone = phone
        self._email = email

        # Load the attachments dataframe
        self._data = self._load()

    def get(self, which: Union[str, Direction]=Direction.ALL) -> pd.DataFrame:
        """Gets the attachments dataframe."""

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

    def get_all(self) -> pd.DataFrame:
        """Gets the unfiltered attachments dataframe."""
        return self._data
    
    def get_sent(self) -> pd.DataFrame:
        """Gets the attachments dataframe filtered by sent messages."""
        return self._data[self._data['is_sender'] == 1]
    
    def get_received(self) -> pd.DataFrame:
        """Gets the attachments dataframe filtered by received messages."""
        return self._data[self._data['is_sender'] == 0]

    def _load(self) -> pd.DataFrame:
        """Loads the attachments dataframe."""
        
        # Query the database depending on what parameters were provided
        chatdb = db.chat.ChatDB(self._path)
        if self._handle_id:
            df = chatdb.get_attachments_from_handle_id(self._handle_id)
        elif self._phone:
            df = chatdb.get_attachments_from_phone(self._phone)
        elif self._email:
            df = chatdb.get_attachments_from_email(self._email)
        else:
            df = chatdb.get_all_attachments()
        return self._clean(df)

    def _clean(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Clean the dataframe to make it more consistent with the library."""
        
        # Convert the date column to datetimes
        dataframe['date'] = dataframe['date'].apply(
            lambda mactime: clean.convert_mactime_to_datetime(mactime)
        )
        
        # Rename the columns
        dataframe = dataframe.rename(columns={
            'date': 'datetime',
            'text': 'message',
        })

        # Set the index to the datetime column and return
        return dataframe.set_index(['datetime'])

    @property
    def path(self) -> Optional[str]:
        """Gets the location of the iMessage database."""
        return self._path
    
    @path.setter
    def path(self, value: Optional[str]):
        """Sets the location of the iMessage database."""
        self._path = value