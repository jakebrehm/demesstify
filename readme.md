<div align="center">
<img src="https://raw.githubusercontent.com/jakebrehm/demesstify/master/img/logo.png" alt="Demesstify Logo" width="600"/>

<br>

<h1>Demystify your messages.</h1>

<br>

<a href="https://github.com/jakebrehm/demesstify"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/jakebrehm/demesstify?color=blue&logo=Git&logoColor=white&style=for-the-badge"></a>
<a href="https://github.com/jakebrehm/demesstify/blob/master/license.txt"><img alt="GitHub license" src="https://img.shields.io/github/license/jakebrehm/demesstify?color=limegreen&style=for-the-badge"></a>
<a href="https://pypi.org/project/demesstify/"><img alt="PyPI" src="https://img.shields.io/pypi/v/demesstify?color=blue&logo=pypi&logoColor=white&style=for-the-badge"></a>
<a href="https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjh4_Onzon8AhWVEVkFHdVmBfwQFnoECBYQAQ&url=https%3A%2F%2Fwww.python.org%2F&usg=AOvVaw0QREvGsjwHKp2GtoYvs1JH"><img alt="Made with Python" src="https://img.shields.io/badge/Made%20with-Python-limegreen?style=for-the-badge&logo=python&logoColor=white"></a>

<br>
</div>

<p align="center">
    <strong>demesstify</strong> is a Python library that demystifies your messages and allows for easy analysis and visualization of conversations.
</p>

<hr>

## Table of contents

* [Installation](#installation)
    * [Dependencies](#dependencies)
* [Example usage](#example-usage)
    * [Basic example](#basic-example)
* [Future improvements](#future-improvements)
* [Authors](#authors)

## Installation

*demesstify* can be installed via pip:

```
pip install demesstify
```

The source code can be viewed on GitHub [here](https://github.com/jakebrehm/demesstify).

### Dependencies

*demesstify* depends on the following packages:

| Package                                                | Description                           |
| ------------------------------------------------------ | ------------------------------------- |
| [pandas](https://github.com/pandas-dev/pandas)         | For easy manipulation of message data |
| [matplotlib](https://github.com/matplotlib/matplotlib) | For visualizations                    |
| [wordcloud](https://github.com/amueller/word_cloud)    | For creating wordclouds               |
| [calmap](https://github.com/martijnvermaat/calmap)    | For creating calendar heatmaps               |
| [emoji](https://github.com/carpedm20/emoji)            | For working with emojis               |
| [lorem](https://github.com/sfischer13/python-lorem)    | For creating dummy text               |

## Example usage

### Basic example

First, import the `demesstify` library.

```python
import demesstify as dm
```

Next, create the iMessages object.

For this example, we will use the `from_random` class method, which allows us to randomly generate the specified number of messages. These messages will be populated using lorem ipsum dummy text.

```python
imessages = dm.iMessages.from_random(total_messages=10)
```

Now that we've created the iMessages object, we can analyze the messages.

For example, we can find the 3 most frequently used emojis and the number of times they appeared in the messages.

```python
imessages.emojis.get_most_frequent(3)
```

Next, we can determine the total number of messages that were exchanged.

```python
imessages.sent.get_total()
```

We can also find the average number of messages received per day.

```python
imessages.received.get_average_per_day()
```

Then, we can calculate the number of times *velit* appears in the messages.

```python
imessages.all.get_count_of_word('velit')
```

For even more analytics, we can create a MessageCloud object.

Because the `MessageCloud` object is essentially a wrapper around the `WordCloud` object of the [wordcloud](https://github.com/amueller/word_cloud) library, we have access to its parameters as well. This way, we can specify exactly what time of words we want to include in the statistics.

```python
cloud = dm.MessageCloud(imessages)
cloud.min_word_length = 3
cloud.repeat = False                # will not repeat any words
cloud.collocations = False          # will not include pairs of words
cloud.include_numbers = False       # will not include numbers
cloud.generate()
```

With the MessageCloud object, we can see which words were used the most frequently and how often.

```python
cloud.words.get_most_frequent(5)
```

## Future improvements

- Add support for identifying attachments
- Add support for other message sources, e.g. Android or social media platforms
- Add more interesting calculations and analyses
- Incorporate sentiment analysis
- Add unit tests

## Authors

- **Jake Brehm** - [Email](mailto:mail@jakebrehm.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)