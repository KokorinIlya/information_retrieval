import re


def is_russian(word):
    return re.match('^[а-яА-ЯёЁ]+$', word) is not None
