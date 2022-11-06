import random


def random_color_func(word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=None):
    h = int(360.0 * 187.0 / 255.0)
    # h = hue
    s = int(100.0 * 255.0 / 255.0)
    l = int(100.0 * float(random_state.randint(60, 120)) / 255.0)

    return f"hsl({h}, {s}%, {l}%)"


def random_gray(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    """Randomly generates a gray hsl color."""

    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def constant_hue(
    hue
):
    """"""

    def _constant_hue(word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=None):
        """"""
        h = hue
        s = int(100.0 * 255.0 / 255.0)
        l = int(100.0 * float(random_state.randint(60, 120)) / 255.0)

        return f"hsl({h}, {s}%, {l}%)"

    return _constant_hue