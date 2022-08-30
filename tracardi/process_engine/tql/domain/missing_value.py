class MissingValue(ValueError):

    def __init__(self, error):
        self.error = error

    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __contains__(self, item):
        return False

    def __ne__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __add__(self, other):
        return other

    def __sub__(self, other):
        return other

    def __truediv__(self, other):
        return 0

    def __mul__(self, other):
        return 0

    def __str__(self):
        return f"Missing Value ({self.error})"
