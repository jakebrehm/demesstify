#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Contains custom errors.
"""


class ReactionNameError(Exception):
    """An exception that is thrown when an invalid reaction name is used."""

    def __init__(self, invalid_name: str, all_names: list[str]):
        """Initializes the ReactionNameError exception."""

        # Store instance variables
        self._invalid_name = invalid_name
        self._all_names = all_names

        # Construct the error message
        error_message = self._construct_message()
        super().__init__(error_message)
    
    def _construct_message(self) -> str:
        """Constructs and returns the error message."""

        message = f"'{self._invalid_name}' is an invalid reaction name. "
        message += f"Valid reaction names are {self._all_names}."
        return message


class CloudNotGeneratedError(Exception):
    """
    An exception that is thrown when trying to access something that requires
    a wordcloud to be generated first.
    """

    def __init__(self):
        """Initializes the CloudNotGeneratedError exception."""

        # Construct the error message
        error_message = "Wordcloud has not yet been generated. "
        error_message += "Please generate using MessageCloud.generate()."
        super().__init__(error_message)