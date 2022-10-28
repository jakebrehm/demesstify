from typing import Union, Set

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from . import parser
from . import errors


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
        self._stopwords = None
        self._mask = None

        self._wordcloud = None

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

    def generate(self):
        ''''''

        if self._messages:
            self._wordcloud = WordCloud()
            self._wordcloud.generate(self._messages)
        else:
            raise ValueError('No messages stored.')


def generate_random_gray(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    ''''''
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)





# text = open('data/output.txt', 'r').read()
# stopwords = set(STOPWORDS)

# # custom_mask = np.array(Image.open('data/manatee_white.png'))
# custom_mask = np.array(Image.open('data/manatee_blur.png'))
# cloud = WordCloud(
#     # background_color='white',
#     # background_color='gray',
#     background_color=(0, 105, 148),
#     stopwords=stopwords,
#     mask=custom_mask,
#     # height=600,
#     # width=400,
#     contour_width=10,
#     # contour_color='black',
#     contour_color='gray',
#     margin=10,
# )
# cloud.generate(text)
# cloud.recolor(color_func=grey_color_func, random_state=3)

# cloud.to_file('data/output.png')
# # plt.imshow(cloud, interpolation='bilinear')
# # plt.axis('off')
# # plt.show()