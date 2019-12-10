import os
import pytest
import shutil

# https://stackoverflow.com/a/44935451
@pytest.fixture(scope="module")
def get_file(request):
    """
    Get the requested file for testing
    """

    # uses .join instead of .dirname so we get a LocalPath object instead of
    # a string. LocalPath.join calls normpath for us when joining the path
    return request.fspath.join("..")


@pytest.fixture(scope="module")
def get_out_dir(request):
    """
    Get the temporary output directory for writing files to
    """

    return request.fspath.join("..") + "/tmp"


@pytest.hookimpl
def pytest_sessionstart(session):
    # shutil.rmtree(session.fspath + "/test/tmp", ignore_errors=True)
    os.mkdir(session.fspath + "/test/tmp")


@pytest.hookimpl
def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(session.fspath + "/test/tmp", ignore_errors=True)
