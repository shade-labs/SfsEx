"""Random filename generation."""

import random

from sex.words import words


def gen_name(n: int = 3):
    """
    Generate a random filename.

    :param n: The number of words to use.
    :return: A random filename.
    """
    return "_".join(random.choices(words, k=n))
