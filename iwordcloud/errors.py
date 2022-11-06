#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Contains custom errors for the 'iwordcloud' project.
"""


from typing import List


class ReactionNameError(Exception):
    """An exception that is thrown when an invalid reaction name is used."""

    def __init__(self, invalid_name: str, all_names: List[str]):
        """Inits the ReactionNameError exception.
        
        Args:
            invalid_name:
                Name of the invalid reaction.
            all_names:
                List of all of the valid reaction names.
        """

        self._invalid_name = invalid_name
        self._all_names = all_names

        error_message = self._construct_message()
        super().__init__(error_message)
    
    def _construct_message(self) -> str:
        """Constructs and returns the error message."""

        message = f"'{self._invalid_name}' is an invalid reaction name. "
        message += f"Valid reaction names are {self._all_names}."
        return message


class MessageArgumentError(Exception):
    """An exception that is thrown when an invalid messages type is used."""

    def __init__(self, message_type: str):
        """Inits the MessageArgumentError exception.
        
        Args:
            message_type:
                The attempted invalid message type.
        """

        error_message = f"Messages type of {message_type} is invalid. "
        error_message += "Must either be of type 'str'"
        error_message += " or 'iwordcloud.parser.iMessages'"
        super().__init__(error_message)


class CloudNotGeneratedError(Exception):
    """
    An exception that is thrown when trying to access something that requires
    a wordcloud to be generated first.
    """

    def __init__(self):
        """Constructs and returns the error message."""

        error_message = "Wordcloud has not yet been generated. "
        error_message += "Please generate using MessageCloud.generate()."
        super().__init__(error_message)