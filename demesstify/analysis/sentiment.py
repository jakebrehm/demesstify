#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for performing sentiment analysis.
"""


import pandas as pd

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ..parser import iMessages


class SentimentAnalyzer(SentimentIntensityAnalyzer):
    """Performs sentiment analysis on message data."""

    def __init__(self, imessages: iMessages, *args, **kwargs):
        """Inits the SentimentAnalyzer instance."""

        # Init the parent class
        super().__init__(*args, **kwargs)

        # Store instance variables
        self._imessages = imessages
    
    def get_average_sentiment(self, whom: str="all"):
        """"""

        # Extract relevant data from iMessages object
        if whom == 'all':
            data = self._imessages.all.get()
        elif whom == 'sender':
            data = self._imessages.sent.get()
        elif whom == 'recipient':
            data = self._imessages.received.get()
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
        

        
