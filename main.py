import iwordcloud as iwc

if __name__ == '__main__':
    input_path = r'data/texts.txt'
    output_path = r'data/output.txt'

    imessages = iwc.iMessages(input_path, own_name='Jake Brehm')
    # imessages.get_all()

    # print(imessages.get_sent())
    # print(imessages.sent)
    
    # imessages.trim('2022-07-02 16:00:00', '2022-07-02 23:59:59')
    # imessages.trim('2022-07-02 00:00:00', '2022-07-02 23:59:59')
    # imessages.trim('2022-07-02 16:00:00', '2022-07-02 18:00:00')
    # print(imessages.sent)

    # for reaction in imessages.reactions:
    #     print(reaction.name)

    # print(imessages.reactions.get_count())
    # print(imessages.reactions.get_count('Loved'))
    # print(imessages.reactions.get_messages('Disliked'))

    # imessages.save_all(output_path)

    cloud = iwc.MessageCloud(imessages)
    cloud.background_color = (0, 105, 148)
    cloud.mask = 'data/manatee_small_blur.png'
    cloud.contour_width = 3
    cloud.contour_color = 'gray'
    cloud.margin = 10
    cloud.generate()
    cloud.recolor(color_func=iwc.color_funcs.random_gray, random_state=3)
    cloud.save('data/output3.png')
    print(cloud.words.get_counts())
    print(cloud.words.get_most_frequent(20))