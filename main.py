"""
Sample code showing how to use the library.
"""


import demesstify as dm
from demesstify.analysis import emojis, sentiment, text
from demesstify.visualize import cloud


def main():
    # Create the messages object and dataframes from dummy text
    messages = dm.Messages.from_random(total_messages=1000)
    all_df = messages.get_all()
    sent_df = messages.get_sent()
    received_df = messages.get_received()

    # Determine the 3 most frequent emojis
    most_frequent_emojis = emojis.Emojis(all_df).get_most_frequent(3)
    print(f"{most_frequent_emojis = }")

    # Determine the total number of messages sent
    total_messages_sent = text.Text(sent_df).get_total()
    print(f"{total_messages_sent = }")

    # Determine the average number of messages received per day
    average_received_daily = text.Text(received_df).get_average_per_day()
    print(f"{average_received_daily = }")

    # Determine the number of times "velit" appear as a substring
    velit_count = text.Text(all_df).get_count_of_substring('velit')
    print(f"{velit_count = }")

    # Determine the average polarity of the messages
    average_polarity = sentiment.Sentiment(all_df).get_average_sentiment()
    print(f"{average_polarity = }")

    # Create and save a Cloud object
    wordcloud = cloud.Cloud(messages.as_string('all'))
    wordcloud.min_word_length = 3
    wordcloud.repeat = False                # will not repeat any words
    wordcloud.collocations = False          # will not include pairs of words
    wordcloud.include_numbers = False       # will not include numbers
    wordcloud.generate()
    wordcloud.save('wordcloud.png')


if __name__ == '__main__':
    main()