import matplotlib.pyplot as plt
import numpy as np
import random
import sys
import os
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

# text = open('data/speech.txt', mode='r', encoding='utf-8').read()
# text = open('data/speech.txt', 'r').read()
text = open('data/output.txt', 'r').read()
stopwords = set(STOPWORDS)

# custom_mask = np.array(Image.open('data/manatee_white.png'))
custom_mask = np.array(Image.open('data/manatee_blur.png'))
cloud = WordCloud(
    # background_color='white',
    # background_color='gray',
    background_color=(0, 105, 148),
    stopwords=stopwords,
    mask=custom_mask,
    # height=600,
    # width=400,
    contour_width=10,
    # contour_color='black',
    contour_color='gray',
    margin=10,
)
cloud.generate(text)
cloud.recolor(color_func=grey_color_func, random_state=3)

cloud.to_file('data/output.png')
# plt.imshow(cloud, interpolation='bilinear')
# plt.axis('off')
# plt.show()

