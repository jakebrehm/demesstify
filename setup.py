import codecs
import os
from setuptools import setup, find_packages

THIS_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
README_PATH = os.path.join(THIS_DIRECTORY, "readme.md")

with codecs.open(README_PATH, encoding="utf-8") as handle:
    long_description = "\n" + handle.read()

VERSION = '2.2.0'
DESCRIPTION = (
    '📱Demystifies your messages and allows for easy analysis '
    'and visualization of conversations.'
)

# Setting up
setup(
    name="demesstify",
    version=VERSION,
    author="Jake Brehm",
    author_email="<mail@jakebrehm.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'pandas', 'matplotlib', 'wordcloud', 'emoji', 'lorem', 'vaderSentiment',
        'calmap',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
    ],
)