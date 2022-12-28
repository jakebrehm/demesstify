#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Stores default settings for the testing module.
"""


from datetime import datetime


# Specify the number of messages
TOTAL_MESSAGES = 100

# Specify the emojis to randomly interject
EMOJIS = ['😊', '😁', '😭', '😘', '😍', '❤️', '👍', '😂', '🤤']
EMOJI_CHANCE = 0.1

# Specify other variables
RECEIVER_NAME = 'Jane Doe'
RECEIVER_PHONE = 15558675309
DATE_FORMAT = r'%b %-d, %Y %H:%M:%S'
START_DATETIME = datetime(2017, 11, 28, 23, 55, 59)
END_DATETIME = datetime(2017, 12, 25, 17, 11, 22)
UNIFORMLY_DISTRIBUTED = False
