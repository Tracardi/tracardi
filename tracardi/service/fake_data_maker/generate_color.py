from random import choice

countries = [
    "white",
    "blue",
    "red",
    "yellow",
    "black",
    "gray",
    "purple",
    "pink",
    "orange",
]


def get_random_color():
    return choice(countries)
