#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for interacting with and extracting messages from
the local iMessage database.
"""


import os
import sqlite3
from typing import Any, Optional

import pandas as pd


class ChatDB:
    """Interacts with the local iMessage database to get messages.
    
    Properties:
        db_location:
            The filepath to the local iMessage database.
    """

    def __init__(self, db_location: Optional[str]=None):
        """Initializes the ChatDB instance.
        
        The chat.db file is located in: ~/Library/Messages/chat.db

        However, this file cannot easily be read unless it is copied and
        pasted somewhere else. It is advised to do this, and then pass the
        new filepath as an argument.

        A workaround to this is to provide full disk access to your terminal,
        IDE, etc. in your system preferences. You will then be able to read the
        database without having to copy and paste it.
        """

        # Use default database location if not specified
        if db_location is None:
            db_location = f"{os.path.expanduser('~')}/Library/Messages/chat.db"
        # Store the database location as an instance variable
        self._db_location = db_location
    
    def get_all_messages(self) -> pd.DataFrame:
        """Gets the dataframe of all messages ever exchanged."""

        # Query the database
        query = """
            SELECT date, is_from_me,  text
            FROM message
            ORDER BY date;
        """
        return self.read_sql_query(query)

    def get_messages_from_handle_id(self, handle_id: int) -> pd.DataFrame:
        """
        Gets the dataframe of all messages with a user that has the
        specified handle ID.

        The handle ID would come from prior knowledge or from deducing it
        by viewing the database directly.
        """

        # Query the database
        query = """
            SELECT date, is_from_me,  text
            FROM message
            WHERE handle_id=?
            ORDER BY date;
        """
        return self.read_sql_query(query, params=(handle_id,))

    def get_messages_from_phone(self, phone: str) -> pd.DataFrame:
        """
        Gets the dataframe of all messages with a user that has the
        specified phone number.
        """

        # Account for the possibility of a plus sign
        if phone[0] != "+":
            phone = f"%{phone}"

        # Return the resulting dataframe
        return self._get_messages_from_id(phone)
    
    def get_messages_from_email(self, email: str) -> pd.DataFrame:
        """
        Gets the dataframe of all messages with a user that has the
        specified email.
        """

        # Return the resulting dataframe
        return self._get_messages_from_id(email)

    def get_all_attachments(self) -> pd.DataFrame:
        """Gets the dataframe of all attachments ever exchanged."""

        # Query the database
        query = """
            SELECT message.date, message.text, message.is_from_me AS is_sender,
                attachment.filename, attachment.transfer_name
            FROM message_attachment_join
            INNER JOIN message
                ON message_attachment_join.message_id=message.ROWID
            INNER JOIN attachment
                ON message_attachment_join.attachment_id=attachment.ROWID
            ORDER BY message.date;
        """
        return self.read_sql_query(query)

    def get_attachments_from_handle_id(self, handle_id: int) -> pd.DataFrame:
        """
        Gets the dataframe of all attachments in a conversation with a user
        that has the specified handle ID.

        The handle ID would come from prior knowledge or from deducing it
        by viewing the database directly.
        """

        # Query the database
        query = """
            SELECT message.date, message.text, message.is_from_me AS is_sender,
                attachment.filename, attachment.transfer_name
            FROM message_attachment_join
            INNER JOIN message
                ON message_attachment_join.message_id=message.ROWID
            INNER JOIN attachment
                ON message_attachment_join.attachment_id=attachment.ROWID
            WHERE message.handle_id LIKE ?
            ORDER BY message.date;
        """
        return self.read_sql_query(query, params=(handle_id,))

    def get_attachments_from_phone(self, phone: str) -> pd.DataFrame:
        """
        Gets the dataframe of all attachments in a conversation with a user
        that has the specified phone number.
        """

        # Account for the possibility of a plus sign
        if phone[0] != "+":
            phone = f"%{phone}"

        # Return the resulting dataframe
        return self._get_attachments_from_id(phone)
    
    def get_attachments_from_email(self, email: str) -> pd.DataFrame:
        """
        Gets the dataframe of all attachments in a conversation with a user
        that has the specified email.
        """

        # Return the resulting dataframe
        return self._get_attachments_from_id(email)

    def _get_messages_from_id(self, id_: str) -> pd.DataFrame:
        """Gets a dataframe of all messages with the specified user."""

        # Query the database
        query = """
            SELECT message.date, message.is_from_me, message.text
            FROM message
            INNER JOIN handle ON message.handle_id=handle.ROWID
            WHERE handle.id LIKE ?
            ORDER BY message.date;
        """
        return self.read_sql_query(query, params=(id_,))

    def _get_attachments_from_id(self, id_: str) -> pd.DataFrame:
        """"""

        # Query the database
        query = """
            SELECT message.date, message.text, message.is_from_me AS is_sender,
                attachment.filename, attachment.transfer_name
            FROM message_attachment_join
            INNER JOIN message
                ON message_attachment_join.message_id=message.ROWID
            INNER JOIN attachment
                ON message_attachment_join.attachment_id=attachment.ROWID
            INNER JOIN handle
                ON message.handle_id=handle.ROWID
            WHERE handle.id LIKE ?
            ORDER BY message.date;
        """
        return self.read_sql_query(query, params=(id_,))

    def read_sql_query(self, query: str, params: Optional[Any]=None) -> pd.DataFrame:
        """Queries with database with a specified SQL command."""

        # Open the connection to the database
        connection = sqlite3.connect(self.db_location)

        # Query the database
        df = pd.read_sql_query(query, connection, params=params)

        # Close the database connection
        connection.close()

        # Return the dataframe
        return df

    @property
    def db_location(self) -> Optional[str]:
        """Gets the location of the iMessage database."""
        return self._db_location
    
    @db_location.setter
    def db_location(self, value: Optional[str]):
        """Sets the location of the iMessage database."""
        self._db_location = value