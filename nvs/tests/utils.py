from pkg_resources import resource_string

DATA_LOCATION = '.'.join(__name__.split('.')[:2] + ['data'])


def get_test_data(path, location=DATA_LOCATION):
    """
    Fetches test data using setuptool's resource_string. Path is relative to
    location which defaults to DATA_LOCATION
    """
    return resource_string(location, path)
