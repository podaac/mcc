
"""
=========================
test_dataset_from_file.py
=========================

Unit tests for the file_utils.get_dataset_from_file() function.

"""

import os
import shutil
import tempfile
from unittest.mock import MagicMock

import netCDF4
import pytest
import werkzeug.exceptions

import mcc.web.file_utils as file_utils


@pytest.fixture(scope="session")
def test_dir():
    """
    Fixture that returns the absolute path of the test directory
    """
    test_dir = os.path.dirname(os.path.realpath(__file__))
    yield test_dir


def setup_function(function):
    # Create a local temp dir we can use to inspect for any temporary files created
    # by get_dataset_from_file()
    local_temp_dir = tempfile.mkdtemp(dir=os.path.dirname(os.path.realpath(__file__)))

    # Point tempfile module used in file_utils.py to use this local temp dir by default
    file_utils.tempfile.tempdir = local_temp_dir

    # Inform the unit test function where the local temp dir is
    function.local_temp_dir = local_temp_dir

    # get_dataset_from_file() utilizes Flask logging, so Mock the app instance out here
    file_utils.app = MagicMock()
    file_utils.app.config = {'MAX_CONTENT_LENGTH': 4295000000}


def test_dataset_from_file(test_dir):
    """Test creation of a NetCDF4 Dataset from an uploaded file, including compressed files"""
    test_data_dir = os.path.join(test_dir, 'data')

    valid_test_cases = [
        ('ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc', 'b15b610e31c96e6593cc4df1f28b078a', '8.32 MB'),  # nominal
        ('ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc.bz2', '1411e11020e54579636ddbf7afc4be93', '2.81 MB'),  # bz2 compression
        ('ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc.gz', 'b55a9ab03692df37c843d72b010b8251', '3.06 MB')  # gzip compression
    ]

    for test_file, expected_hash, expected_size in valid_test_cases:
        test_file_path = os.path.join(test_data_dir, test_file)

        with open(test_file_path, 'rb') as infile:
            infile.filename = test_file
            result = file_utils.get_dataset_from_file(infile)

        # Ensure returned dictionary conforms to what we expect
        assert isinstance(result, dict)

        assert 'dataset' in result
        assert isinstance(result['dataset'], netCDF4.Dataset)

        assert 'hash' in result
        assert result['hash'] == expected_hash

        assert 'size' in result
        assert result['size'] == expected_size

        assert 'filename' in result
        assert result['filename'] == test_file

        # Ensure all temporary files written by get_dataset_from_file() within
        # the local temp directory created by this test suite have been
        # deleted now that the function has returned
        assert len(os.listdir(test_dataset_from_file.local_temp_dir)) == 0

    # For each of the invalid test files, ensure that we raise an exception
    # and that there are no temporary files remaining on disk afterward
    invalid_test_files = [
        'ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc.invalid_zip.gz',  # unsupported compression
        'invalid_archive.h5',  # unsupported format for NetCDF4
        'unsupported_archive.nc3'  # unsupported file extension
    ]

    for test_file in invalid_test_files:
        test_file_path = os.path.join(test_data_dir, test_file)

        with open(test_file_path, 'rb') as infile:
            infile.filename = test_file
            with pytest.raises(werkzeug.exceptions.InternalServerError):
                file_utils.get_dataset_from_file(infile)

        assert len(os.listdir(test_dataset_from_file.local_temp_dir)) == 0


def teardown_function(function):
    # Remove the local temp directory
    if os.path.exists(function.local_temp_dir):
        shutil.rmtree(function.local_temp_dir)

