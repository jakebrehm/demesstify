#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the attachments that
were exchanged in a given message conversation.
"""


from typing import Optional, Union

import pandas as pd

from .. import database as db
from .. import clean
from ..parse import Direction


class Attachment:
    """Analyzes attachments data."""

    def __init__(self, data: pd.DataFrame):
        """Initializes the Attachment object."""

        self._data = data

    def get_count(self) -> int:
        """Gets the number of attachments that were exchanged."""
        return len(self._data)


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
            'test': 'message',
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