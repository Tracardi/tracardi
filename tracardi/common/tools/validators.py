import urllib.parse


def is_valid_url(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc])
    except ValueError:
        return False


def is_valid_hex(string):
    # Check if the string has exactly 2 characters and they are alphanumeric
    if len(string) == 2 and string.isalnum():
        # Check if both characters are lowercase hexadecimal digits
        return all(char.lower() in '0123456789abcdef' for char in string)
    return False
