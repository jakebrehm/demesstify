#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for performing sentiment analysis.
"""


import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from ..parse import Messages


class SentimentAnalyzer(SentimentIntensityAnalyzer):
    """Performs sentiment analysis on message data."""

    def __init__(self, messages: Messages, *args, **kwargs):
        """Inits the SentimentAnalyzer instance."""

        # Init the parent class
        super().__init__(*args, **kwargs)

        # Store instance variables
        self._messages = messages
    
    def get_average_sentiment(self, whom: str="all"):
        """"""

        # Extract relevant data from the Messages object
        if whom == 'all':
            data = self._messages.all.get()
        elif whom == 'sender':
            data = self._messages.sent.get()
        elif whom == 'recipient':
            data = self._messages.received.get()
        else:
            raise ValueError(f"'{whom}' is not a valid value for 'whom'.")
        
        # Generate pandas series of compound polarity scores
        polarities = pd.Series(
            data['message'].apply(
                lambda text: self.polarity_scores(text)['compound']
            )
        )

        # Return the average polarity
        return polarities.mean()
        

        
