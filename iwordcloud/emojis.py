import collections
from typing import List, Dict, Tuple

import emoji
import pandas as pd


class Emoji:
    """"""

    def __init__(
            self, emoji: str, messages: pd.DataFrame,
            imessages: 'parser.iMessages'
        ):
        """"""

        self._emoji = emoji
        self._messages = messages
        self._imessages = imessages

    @property
    def name(self) -> str:
        """"""
        return self._emoji

    def get_count(self, which: str='all') -> int:
        """"""

        if which == 'all':
            return self.get_all_count()
        elif which == 'sent':
            return self.get_sent_count()
        elif which == 'received':
            return self.get_received_count()
        else:
            raise ValueError(f"{which} is not a valid value for 'which'.")

    def get_all_count(self) -> int:
        """"""

        return self._count_emojis(self._messages)

    def get_all_messages(self) -> pd.DataFrame:
        """"""

        return self._messages
    
    def get_sent_messages(self) -> pd.DataFrame:
        """"""

        messages = self.get_all_messages()
        return messages[messages['sender'] == self._imessages.own_name]
    
    def get_sent_count(self) -> int:
        """"""

        return self._count_emojis(self.get_sent_messages())
    
    def get_received_messages(self) -> pd.DataFrame:
        """"""

        messages = self.get_all_messages()
        return messages[messages['sender'] != self._imessages.own_name]
    
    def get_received_count(self) -> int:
        """"""

        return self._count_emojis(self.get_received_messages())
    
    def _count_emojis(self, df: pd.DataFrame) -> int:
        """"""

        return df['message'].str.count(self.name).sum()

class Emojis:
    """"""

    def __init__(self, imessages: 'parser.iMessages'):
        """"""

        self._imessages = imessages

        messages = self._imessages.get_all()
        self._unique_emojis = emoji.distinct_emoji_list(messages)
        self._emoji_objects = self._create_emoji_objects(self._unique_emojis)
        self._counts = self._count_emojis(self._emoji_objects)

    def get_uniques(self) -> List[str]:
        """"""

        return self._unique_emojis
    
    def get_count(self, emoji: str) -> int:
        """"""

        return self._counts[emoji]

    def get_counts(self) -> Dict[str, int]:
        """"""

        return self._counts

    def get_most_frequent(self, n: int) -> List[Tuple[str, int]]:
        """"""

        counter = collections.Counter(self.get_counts())
        return counter.most_common(n)

    def _count_emojis(self, emoji_objects: Dict[str, Emoji]):
        """"""

        counts = {}
        for emoji_name, emoji_object in emoji_objects.items():
            counts[emoji_name] = emoji_object.get_count()
        return counts

    def _create_emoji_objects(self, emojis: str) -> Dict[str, Emoji]:
        """"""

        messages = self._imessages.data
        emoji_objects = {}
        for emoji in emojis:
            df = messages[messages['message'].str.contains(emoji)]
            # Need to count multiple emojis in single line
            emoji_object = Emoji(emoji, messages=df, imessages=self._imessages)
            emoji_objects[emoji] = emoji_object
        return emoji_objects
    
    def __getitem__(self, emoji: str) -> Emoji:
        """"""

        return self._emoji_objects[emoji]