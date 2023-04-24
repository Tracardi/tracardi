from random import choice

interests = [
    "sports",
    "swimming",
    "cooking",
    "running",
    "travel",
    "media",
    "games",
    "gardening",
    "IT",
]


def get_random_interest():
    return {"interest": choice(interests)}
