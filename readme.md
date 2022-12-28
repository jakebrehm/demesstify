<div align="center">
<img src="https://raw.githubusercontent.com/jakebrehm/demesstify/master/img/logo.png" alt="Demesstify Logo" width="600"/>

<br>

<h1>Demystify your messages.</h1>

<br>

<a href="https://github.com/jakebrehm/demesstify"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/jakebrehm/demesstify?color=blue&logo=Git&logoColor=white&style=for-the-badge"></a>
<a href="https://github.com/jakebrehm/demesstify/blob/master/license.txt"><img alt="GitHub license" src="https://img.shields.io/github/license/jakebrehm/demesstify?color=limegreen&style=for-the-badge"></a>
<a href="https://pypi.org/project/demesstify/"><img alt="PyPI Page" src="https://img.shields.io/pypi/v/demesstify?color=blue&logo=pypi&logoColor=white&style=for-the-badge"></a>
<a href="https://pypistats.org/packages/demesstify"><img alt="PyPI Downloads" src="https://img.shields.io/pypi/dm/demesstify?color=limegreen&logo=pypi&logoColor=white&style=for-the-badge"></a>

<br>
</div>

<p align="center">
    <strong>demesstify</strong> is a Python library that demystifies your messages and allows for easy analysis and visualization of conversations.
</p>

<hr>

## Table of contents

* [Main features](#main-features)
* [Installation](#installation)
    * [Dependencies](#dependencies)
* [Example usage](#example-usage)
    * [Analyzing the messages](#analyzing-the-messages)
    * [Creating a word cloud](#creating-a-word-cloud)
* [Future improvements](#future-improvements)
* [Authors](#authors)

## Main features

Here are just a few things that `demesstify` can do:
* Read message data from various sources, including your local iMessages database, a [Tansee](https://www.tansee.com) text file, or some randomly generated dummy text
* Perform text analysis on your messages so you can see things like the average number of texts received per day or the most number of messages that were sent in a row
* Analyze which emojis or reactions (if you're using iMessage) were most frequently used, among other thing
* Perform sentiment analysis on your messages to see the polarity of your conversations
* Generate tailored visualizations such as word clouds or a radial heatmap that plots hour of the day versus day of the week

## Installation

`demesstify` can be installed via pip:

```
pip install demesstify
```

The source code can be viewed on GitHub [here](https://github.com/jakebrehm/demesstify).

### Dependencies

`demesstify` depends on the following packages:

| Package                                                | Description                           |
| ------------------------------------------------------ | ------------------------------------- |
| [pandas](https://github.com/pandas-dev/pandas)         | For easy manipulation of message data |
| [matplotlib](https://github.com/matplotlib/matplotlib) | For visualizations                    |
| [wordcloud](https://github.com/amueller/word_cloud)    | For creating wordclouds               |
| [vaderSentiment](https://github.com/cjhutto/vaderSentiment)    | For sentiment analysis               |
| [calmap](https://github.com/martijnvermaat/calmap)    | For creating calendar heatmaps               |
| [emoji](https://github.com/carpedm20/emoji)            | For working with emojis               |
| [lorem](https://github.com/sfischer13/python-lorem)    | For creating dummy text               |

## Example usage

### Analyzing the messages

```python
import demesstify as dm
from demesstify.analysis import emojis, sentiment, text

# Create the messages object and dataframes from dummy text
messages = dm.Messages.from_random(total_messages=1000)
all_df = messages.get_all()
sent_df = messages.get_sent()
received_df = messages.get_received()

# Determine the 3 most frequent emojis
most_frequent_emojis = emojis.Emojis(all_df).get_most_frequent(3)

# Determine the total number of messages sent
total_messages_sent = text.Text(sent_df).get_total()

# Determine the average number of messages received per day
average_received_daily = text.Text(received_df).get_average_per_day()

# Determine the number of times "velit" appear as a substring
velit_count = text.Text(all_df).get_count_of_substring('velit')

# Determine the average polarity of the messages
average_polarity = sentiment.Sentiment(all_df).get_average_sentiment()
```

### Creating a word cloud

```python
import demesstify as dm
from demesstify.visualize import cloud

# Create and save a Cloud object
wordcloud = cloud.Cloud(messages.as_string('all'))
wordcloud.min_word_length = 3
wordcloud.repeat = False                # will not repeat any words
wordcloud.collocations = False          # will not include pairs of words
wordcloud.include_numbers = False       # will not include numbers
wordcloud.generate()
wordcloud.save('wordcloud.png')
```

<div align="center">
<img src="https://raw.githubusercontent.com/jakebrehm/demesstify/master/img/wordcloud.png" alt="Sample WordCloud"/>
</div>


## Future improvements

- Add support for identifying attachments
- Add support for other message sources, e.g. Android or social media platforms
- Add unit tests

## Authors

- **Jake Brehm** - [Email](mailto:mail@jakebrehm.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)