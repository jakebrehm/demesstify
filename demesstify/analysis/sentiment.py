#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides functionality for performing sentiment analysis.
"""


import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from ..parse import Direction, Messages


class Sentiment(SentimentIntensityAnalyzer):
    """Performs sentiment analysis on message data."""

    def __init__(self, data: pd.DataFrame, *args, **kwargs):
        """Initializes the Sentiment instance."""

        # Init the parent class
        super().__init__(*args, **kwargs)

        # Store instance variables
        self._data = data
    
    def get_average_sentiment(self) -> float:
        """Gets the average sentiment of the data."""
        
        # Generate pandas series of compound polarity scores
        polarities = pd.Series(
            self._data['message'].apply(
                lambda text: self.polarity_scores(text)['compound']
            )
        )

        # Return the average polarity
        return polarities.mean().item()
