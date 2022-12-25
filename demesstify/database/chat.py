#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for interacting with the local iMessage database.
"""


import os
import sqlite3

import pandas as pd


class ChatDB:
    """Interacts with the local iMessage database."""

    def __init__(self, db_location: str):
        """Inits the ChatDB instance.
        
        The chat.db file is located in: ~/Library/Messages/chat.db

        However, this file cannot be read unless it is copied and pasted
        somewhere else.
        """

        # Use default database location if not specified
        if db_location is None:
            db_location = f"{os.path.expanduser('~')}/Library/Messages/chat.db"
        # Store the database location as an instance variable
        self._db_location = db_location
    
    def get_from_handle_id(self, handle_id: int) -> pd.DataFrame:
        """
        Returns the dataframe of all messages with a user that has the
        specified handle ID.

        The handle ID would come from prior knowledge or from deducing it
        by viewing the database directly.
        """

        # Open the connection to the database
        connection = sqlite3.connect(self.db_location)

        # Query the database
        query = f"""
            SELECT date, is_from_me,  text
            FROM message
            WHERE handle_id=?
            ORDER BY date;
        """
        df = pd.read_sql_query(query, connection, params=(handle_id,))

        # Close the database connection
        connection.close()

        # Return the dataframe
        return df
    
    def get_from_phone(self, phone: str) -> pd.DataFrame:
        """
        Returns the dataframe of all messages with a user that has the
        specified phone number.
        """

        # Account for the possibility of a plus sign
        if phone[0] != "+":
            phone = f"%{phone}"

        # Return the resulting dataframe
        return self._get_from_id(phone)
    
    def get_from_email(self, email: str) -> pd.DataFrame:
        """
        Returns the dataframe of all messages with a user that has the
        specified email.
        """

        # Return the resulting dataframe
        return self._get_from_id(email)
    
    def _get_from_id(self, id_: str) -> pd.DataFrame:
        """Returns a dataframe of all messages with the specified user."""

        # Open the connection to the database
        connection = sqlite3.connect(self.db_location)

        # Query the database
        query = f"""
            SELECT message.date, message.is_from_me, message.text
            FROM message
            INNER JOIN handle ON message.handle_id=handle.ROWID
            WHERE handle.id LIKE ?
            ORDER BY date;
        """
        df = pd.read_sql_query(query, connection, params=(id_,))

        # Close the database connection
        connection.close()

        # Return the dataframe
        return df

    @property
    def db_location(self) -> str:
        """Gets the location of the iMessage database."""
        return self._db_location
    
    @db_location.setter
    def db_location(self, value: str):
        """Sets the location of the iMessage database."""
        self._db_location = value