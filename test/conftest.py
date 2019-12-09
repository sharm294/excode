import pytest

# https://stackoverflow.com/a/44935451
@pytest.fixture(scope="module")
def get_file(request):
    """
    Get the requested file for testing
    """

    # uses .join instead of .dirname so we get a LocalPath object instead of
    # a string. LocalPath.join calls normpath for us when joining the path
    return request.fspath.join("..")
