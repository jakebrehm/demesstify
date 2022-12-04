import iwordcloud as iwc


if __name__ == '__main__':

    # Create the iMessages object
    imessages = iwc.iMessages.from_random(total_messages=10)

    # Determine the 3 most frequent emojis
    most_frequent_emojis = imessages.emojis.get_most_frequent(3)
    print(most_frequent_emojis)

    # Determine the total number of messages exchanged
    total_messages = imessages.sent.get_total()
    print(total_messages)

    # Determine the average number of messages received per day
    average_received = imessages.received.get_average_per_day()
    print(average_received)

    # Determine the number of times "velit" appears in the messages
    velit_count = imessages.all.get_count_of_word('velit')
    print(velit_count)

    # Create a MessageCloud object
    cloud = iwc.MessageCloud(imessages)
    cloud.min_word_length = 3
    cloud.repeat = False                # will not repeat any words
    cloud.collocations = False          # will not include pairs of words
    cloud.include_numbers = False       # will not include numbers
    cloud.generate()

    # Determine the 5 most frequent words
    most_frequent_words = cloud.words.get_most_frequent(5)
    print(most_frequent_words)