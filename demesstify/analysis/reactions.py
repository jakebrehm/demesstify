#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the reactions that occur in
a given message conversation.
"""


import re
from typing import Optional, Union

import pandas as pd

from .. import errors


REACTION_NAMES = [
    'Liked',
    'Disliked',
    'Loved',
    'Laughed at',
    'Emphasized',
    'Questioned',
]


def get_reaction_names() -> list[str]:
    """Gets the list of possible reaction names."""
    return REACTION_NAMES


class Reaction:
    """Class for a generic iMessage reaction message.
    
    Properties:
        name:
            The name of the reaction.
        messages:
            Dataframe of messages that include this reaction.
    """

    def __init__(self, name: str):
        """Inititalizes the Reaction object."""

        # Store instance variables
        self._name = name

        # Initialize the data dataframe
        self._data = pd.DataFrame()

    @property
    def name(self) -> str:
        """Gets the name of the reaction."""
        return self.get_name()

    @property
    def messages(self) -> pd.DataFrame:
        """Gets the messages dataframe."""
        return self.get_messages()

    def get_name(self) -> str:
        """Gets the name of the reaction."""
        return self._name

    def get_messages(self) -> pd.DataFrame:
        """Gets the messages dataframe."""
        return self._data
    
    def set_messages(self, messages: pd.DataFrame):
        """Sets the messages dataframe."""
        self._data = messages

    def append_messages(self, new_messages: pd.DataFrame):
        """Appends a new messages dataframe to the existing dataframe."""
        self._data = pd.concat([self._data, new_messages])
    
    def get_count(self) -> int:
        """Gets the number of times the reaction has appeared."""
        return len(self._data)

    def __repr__(self) -> str:
        """Returns a representation of an instance of Reaction."""
        return f"{self.__class__.__name__}('{self.name}')"

    def __str__(self) -> str:
        """Returns a string representation of the reaction."""
        return self.name


class Reactions:
    """Collection of Reaction objects.
    
    Properties:
        reactions:
            List of reaction objects.
    """

    def __init__(self, data: pd.DataFrame=None):
        """Initializes the Reactions object, with message data if specified."""

        # Create reaction objects
        self._reactions = self._create_reaction_objects()

        # Update the stored data
        if data is not None:
            self.update(data)

    @property
    def reactions(self) -> list[Reaction]:
        """Returns a list of reaction objects."""
        return self.get_reaction_objects()

    def get_reaction_objects(self) -> list[Reaction]:
        """Returns a list of reaction objects."""
        return list(self._reactions.values())

    def get_count(self, name: str=None) -> Union[dict[str, int], int]:
        """
        Gets the count of the specified reaction, or a dictionary of
        reactions and their corresponding counts if no reaction name is
        specified.
        """

        if not name:
            # If no name is specified, return counts of all reactions
            return self._get_counts()
        else:
            # Otherwise, check if the specified name is valid
            if name in REACTION_NAMES:
                # If it is, return the count of the specified reaction
                return self[name].get_count()
            else:
                # Otherwise, raise an exception
                raise errors.ReactionNameError(name, REACTION_NAMES)

    def get_messages(self, name: str=None) -> pd.DataFrame:
        """
        Gets a dataframe filtered by the specified reaction name, or all 
        reaction names if no name is given.
        """
        
        if not name:
            # If no name is specified, return the messages of all reactions
            messages = pd.DataFrame()
            for name in self:
                messages = pd.concat([messages, name.get_messages()])
            return messages
        else:
            # If it is, return the messages of the specified reaction
            if name in REACTION_NAMES:
                return self[name].get_messages()
            else:
                # Otherwise, raise an exception
                raise errors.ReactionNameError(name, REACTION_NAMES)

    def update(self, dataframe: pd.DataFrame):
        """Adds messages from the supplied dataframe to each reaction object."""

        for reaction in self:
            data = dataframe[dataframe['reaction'] == reaction.name]
            reaction.set_messages(data)

    @staticmethod
    def get_reaction(line: str) -> Optional[str]:
        """Gets the name of the reaction if there is one."""

        for name in REACTION_NAMES:
            # Determine if the line is a reaction message
            search = re.match(fr'^{name} \"(.*)\"$', line)
            if search:
                # If so, return the name of the reaction
                return name
        # Otherwise, return None
        return None

    def _create_reaction_objects(self) -> dict[str, Reaction]:
        """Returns a dictionary of reaction objects."""
        return {name: Reaction(name) for name in REACTION_NAMES}
    
    def _get_counts(self) -> dict[str, int]:
        """Returns a dictionary of reactions and their corresponding counts."""
        return {name: r.get_count() for name, r in self._reactions.items()}

    def __getitem__(self, name: str) -> Reaction:
        """Returns the reaction object with the specified name."""
        return self._reactions[name]

    def __iter__(self):
        """Returns an iterable reactions object."""
        return ReactionsIterable(self.reactions)


class ReactionsIterable:
    """An iterable reactions object."""

    def __init__(self, reactions: Reactions):
        """Initializes the ReactionsIterable object."""

        # Store instance variables
        self._reactions = reactions

        # Initialize calculated instance variables
        self._number_of_reactions = len(self._reactions)
        self._current_index = 0
    
    def __iter__(self):
        """Returns the iterable object."""
        return self
    
    def __next__(self) -> Reaction:
        """Moves to the next reaction object."""

        if self._current_index < self._number_of_reactions:
            # Increment the index and return the reaction
            reaction = self._reactions[self._current_index]
            self._current_index += 1
            return reaction
        raise StopIteration