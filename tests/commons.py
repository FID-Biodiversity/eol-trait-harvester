import requests


def internet_connection_available():
    """ Returns True, if an internet connection is available. """
    try:
        requests.get("https://www.duckduckgo.com/")
        return True
    except requests.exceptions.ConnectionError:
        return False
