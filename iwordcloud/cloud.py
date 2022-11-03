import collections
import random
from typing import Callable, List, Dict, Tuple, Set, Union

import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from . import parser
from . import errors


def requires_cloud(method):
    ''''''

    def inner(self, *args, **kwargs):
        if self.is_valid() is None:
            raise errors.CloudNotGeneratedError()
        else:
            return method(self, *args, **kwargs)
    return inner


class MessageCloud:
    ''''''

    def __init__(self, messages: Union[str, parser.iMessages]=None):
        ''''''

        if messages is None:
            self._messages = None
        elif isinstance(messages, str):
            self.feed_text_file(messages)
        elif isinstance(messages, parser.iMessages):
            self.feed_imessages(messages)
        else:
            raise errors.MessageArgumentError(type(messages))
        
        self._background_color = (0, 105, 148) # TODO: find a better default
        self._stopwords = STOPWORDS
        self._mask = None
        self._height = None
        self._width = None
        self._contour_width = None
        self._contour_color = None
        self._margin = None

        self._wordcloud = None
        self._words = Words()

    @property
    def words(self) -> 'Words':
        ''''''
        return self._words

    def feed_text_file(self, path: str):
        ''''''

        with open(path, 'r') as text:
            self._messages = text.read()

    def feed_imessages(self, imessages: parser.iMessages):
        ''''''

        self._messages = imessages.get_all()

    def set_background_color(self, *args: int):
        ''''''

        if len(args) != 3:
            raise ValueError('Invalid number of arguments.')

        self._background_color = tuple(args)

    def set_stopwords(self, words: Set[str]):
        ''''''

        self._stopwords = words

    def set_image_mask(self, path: str):
        ''''''

        self._mask = np.array(Image.open(path))

    def set_height(self, height: int):
        ''''''

        self._height = height

    def set_width(self, width: int):
        ''''''

        self._width = width

    def set_contour_width(self, width: int):
        ''''''

        self._contour_width = width
    
    def set_contour_color(self, color: str):
        ''''''

        self._contour_color = color
    
    def set_margin(self, margin: int):
        ''''''

        self._margin = margin

    def generate(self):
        ''''''

        if self._messages:

            kwargs = {}
            if self._background_color is not None:
                kwargs.update({'background_color': self._background_color})
            if self._stopwords is not None:
                kwargs.update({'stopwords': self._stopwords})
            if self._mask is not None:
                kwargs.update({'mask': self._mask})
            if self._height is not None:
                kwargs.update({'height': self._height})
            if self._width is not None:
                kwargs.update({'width': self._width})
            if self._contour_width is not None:
                kwargs.update({'contour_width': self._contour_width})
            if self._contour_color is not None:
                kwargs.update({'contour_color': self._contour_color})
            if self._margin is not None:
                kwargs.update({'background_color': self._background_color})

            self._wordcloud = WordCloud(
                **kwargs
                # background_color=self._background_color,
                # stopwords=self._stopwords,
                # mask=self._mask,
                # height=self._height,
                # width=self._width,
                # contour_width=self._contour_width,
                # contour_color=self._contour_color,
                # margin=self._margin,
            )
            self._wordcloud.generate(self._messages)
            self._words.update(self)
        else:
            raise ValueError('No messages stored.')

    def recolor(self, color_func: Callable, random_state: int):
        ''''''

        self._wordcloud.recolor(color_func=color_func, random_state=random_state)

    def save(self, path: str):
        ''''''

        self._wordcloud.to_file(path)


class Words:
    ''''''

    def __init__(self, messagecloud: MessageCloud=None):
        ''''''

        if messagecloud is not None:
            self.update(messagecloud)
        else:
            self._messagecloud = None
            self._wordcloud = None
            self._messages = None

    def is_valid(self) -> bool:
        ''''''

        attributes = [self._messagecloud, self._wordcloud, self._messages]
        return all(attribute is not None for attribute in attributes)

    def update(self, messagecloud: MessageCloud):
        ''''''

        self._messagecloud = messagecloud
        self._wordcloud = self._messagecloud._wordcloud
        self._messages = self._messagecloud._messages
    
    @requires_cloud
    def get_counts(self) -> Dict[str, int]:
        ''''''

        return self._wordcloud.process_text(self._messages)

    @requires_cloud
    def get_most_frequent(self, n: int) -> List[Tuple[str, int]]:
        ''''''

        counter = collections.Counter(self.get_counts())
        return counter.most_common(n)


def generate_random_gray(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    ''''''
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)
