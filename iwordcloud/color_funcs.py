import random


def random_gray(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    """Randomly generates a gray hsl color."""

    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)