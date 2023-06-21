import urllib.parse


def is_valid_url(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc])
    except ValueError:
        return False
