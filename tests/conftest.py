import os
import pytest
import tempfile
from pwd import getpwuid

TEMP_DIRECTORY = 'tempdir'
TESTS_FILENAME_PREFIX = 'tests_'

def find_owner(filename):
    return getpwuid(os.lstat(filename).st_uid).pw_name

def file_info(file_name):
    info = os.lstat(file_name)
    return oct(info.st_mode)

@pytest.fixture()
def mk_temp_file(delete = False):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_path = os.path.join(current_dir, TEMP_DIRECTORY)
    return tempfile.NamedTemporaryFile(dir=temp_path, prefix=TESTS_FILENAME_PREFIX, delete=delete)

@pytest.fixture()
def make_temp_file_without_run_permissions(mk_temp_file):
    os.chmod(mk_temp_file.name, 0o444)
    yield mk_temp_file
    print(f'Removed file {mk_temp_file.name} with perm {file_info(mk_temp_file.name)}')
    os.remove(mk_temp_file.name)


if __name__ == '__main__':
    pass
