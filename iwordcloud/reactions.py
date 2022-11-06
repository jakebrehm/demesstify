#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for tracking and analyzing the reactions that occur in
a given iMessage conversation.
"""


import re
from typing import List, Tuple, Dict, Optional, Union

import pandas as pd

from . import errors


class Reaction:
    """Class for a generic iMessage reaction message.
    
    Properties:
        name:
            The name of the reaction.
        messages:
            Dataframe of messages that include this reaction.
    """

    def __init__(self, name: str):
        """Inits the Reaction object.
        
        Args:
            name:
                The name of the reaction.
        """

        self._name = name
        self._messages = pd.DataFrame()

    @property
    def name(self) -> str:
        """Returns the name of the reaction."""
        return self.get_name()

    @property
    def messages(self) -> pd.DataFrame:
        """Returns the messages dataframe."""
        return self.get_messages()

    def get_name(self) -> str:
        """Returns the name of the reaction."""
        return self._name

    def get_messages(self) -> pd.DataFrame:
        """Returns the messages dataframe."""
        return self._messages
    
    def set_messages(self, messages: pd.DataFrame):
        """Sets or overwrites the messages dataframe."""
        self._messages = messages

    def append_messages(self, new_messages: pd.DataFrame):
        """Appends a new messages dataframe to the existing dataframe.
        
        Args:
            new_messages:
                The new messages dataframe to append.
        """
        
        self._messages = pd.concat([self._messages, new_messages])
    
    def get_count(self) -> int:
        """Returns the number of times the reaction has appeared."""
        return len(self._messages)


class Reactions:
    """Collection of Reaction objects.
    
    Properties:
        names:
            List of reaction names.
        reactions:
            List of reaction objects.
    """

    _REACTIONS = [
        'Liked',
        'Disliked',
        'Loved',
        'Laughed at',
        'Emphasized',
        'Questioned',
    ]

    def __init__(self, messages: pd.DataFrame=None):
        """Inits the Reactions object, with message data if specified."""

        self._reactions = self._create_reaction_objects()
        if messages is not None:
            self.update(messages)
    
    @property
    def names(self) -> List[str]:
        """Returns a list of reaction names."""
        return self.get_reaction_names()

    @property
    def reactions(self) -> List[Reaction]:
        """Returns a list of reaction objects."""
        return self.get_reaction_objects()

    def get_reaction_names(self) -> List[str]:
        """Returns a list of reaction names."""
        return self._REACTIONS

    def get_reaction_objects(self) -> List[Reaction]:
        """Returns a list of reaction objects."""
        return list(self._reactions.values())

    def get_count(self, name: str=None) -> Union[Dict[str, int], int]:
        """
        Returns the count of the specified reaction, or a dictionary of
        reactions and their corresponding counts if no reaction name is
        specified.

        Args:
            name:
                The name of the reaction to return the count of.
        """

        if not name:
            # If no name is specified, return counts of all reactions
            return self._get_counts()
        else:
            # Otherwise, check if the specified name is valid
            if name in self.names:
                # If it is, return the count of the specified reaction
                return self[name].get_count()
            else:
                # Otherwise, raise an exception
                raise errors.ReactionNameError(name, self.names)

    def get_messages(self, name: str=None) -> Union[List[str], pd.DataFrame]:
        """
        Returns the messages of the specified reaction, or a dictionary of
        reactions and their corresponding messages if no reaction name is
        specified.

        Args:
            name:
                The name of the reaction to return the count of.
        """
        
        if not name:
            # If no name is specified, return the messages of all reactions
            messages = pd.DataFrame()
            for name in self:
                messages = pd.concat([messages, name.get_messages()])
            return messages
        else:
            # If it is, return the messages of the specified reaction
            if name in self.names:
                return self[name].get_messages()
            else:
                # Otherwise, raise an exception
                raise errors.ReactionNameError(name, self.names)

    def update(self, dataframe: pd.DataFrame):
        """Adds messages to each reaction object from the supplied dataframe."""

        for reaction in self:
            data = dataframe[dataframe['reaction'] == reaction.name]
            reaction.set_messages(data)

    @staticmethod
    def is_reaction(line: str) -> Tuple[Optional[str], str]:
        """Determines if the line is a reaction message.
        
        Returns a tuple in the form (reaction name, message reacted to).
        However, if the line is determined to not be a reaction message,
        the reaction name will be None.
        """

        for name in Reactions._REACTIONS:
            # Determine if the line is a reaction message
            search = re.match(fr'^{name} \"(.*)\"$', line)
            if search:
                # If so, return the reaction and the message being reacted to
                return name, search.group(1)
        # Otherwise, just return the original line
        return None, line

    def _create_reaction_objects(self) -> Dict[str, Reaction]:
        """Returns a dictionary of reaction objects."""
        return {name: Reaction(name) for name in self._REACTIONS}
    
    def _get_counts(self) -> Dict[str, int]:
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
        """Inits the ReactionsIterable object.
        
        args:
            reactions:
                List of reaction objects to iterate over.
        """

        self._reactions = reactions
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