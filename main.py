import iwordcloud as iwc


if __name__ == '__main__':
    # Specify input and output paths
    input_path = r'data/texts.txt'
    output_path = r'data/output.txt'

    # Create the iMessages object
    imessages = iwc.iMessages(input_path, own_name='Jake Brehm')

    # Create the WordCloud object and set parameters
    cloud = iwc.MessageCloud(imessages)

    # Settings for the word cloud generation for easy changes
    CONTOUR = False

    # Set the word cloud's background color
    # cloud.background_color = (85, 219, 237) # Hannah's favorite color
    cloud.background_color = (255, 255, 255)

    # Specify the font and related settings to be used for the word cloud
    # cloud.font_path = 'DIN Condensed Bold'
    cloud.font_path = 'RobotoCondensed-Regular'
    # cloud.font_path = 'Bell MT'
    cloud.min_font_size = 4
    cloud.max_font_size = 96

    # Set the custom mask for the word cloud and well as its contour
    cloud.mask = 'data/manatee_small_blur.png'
    if CONTOUR:
        cloud.contour_width = 2
        cloud.contour_color = (85, 219, 237)
        cloud.margin = 5

    # Define the number of words to be shown in the word cloud
    cloud.max_words = 400

    # Word processing settings
    cloud.min_word_length = 2
    cloud.collocations = False          # will not include pairs of words
    cloud.include_numbers = False       # will not include numbers

    # Generate the word cloud and recolor
    cloud.generate()
    cloud.recolor(color_func=iwc.color_funcs.constant_hue(187), random_state=3)

    # Save the word cloud to a file
    cloud.save('data/output.png')