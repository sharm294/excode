import os
import pytest
import shutil
import subprocess

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
    # test using invalid arguments (non existent input file)
    subprocess.run(["excode dummy_file test/tests"], shell=True)

    # test running excode on a single file to a directory that already exists
    os.makedirs("test/test_one")
    subprocess.run(["excode test/markdown/concat.md test/test_one"], shell=True)
    shutil.rmtree(session.fspath + "/test/test_one", ignore_errors=True)

    # the "normal" launch of excode
    subprocess.run(["excode test/markdown test/tests"], shell=True)


@pytest.hookimpl
def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(session.fspath + "/test/tests", ignore_errors=True)
