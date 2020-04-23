from typing import NamedTuple


class Match(NamedTuple):
    letter: str


class Replacement(NamedTuple):
    letter_from: str
    letter_to: str


class Insertion(NamedTuple):
    letter: str


class Removal(NamedTuple):
    letter: str
