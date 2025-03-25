"""
=====================
test_cf1_7_checker.py
=====================

This test runs a NC file against both CF 1.6 and 1.7 Conventions to produce CF
Checker report that is according to the Convention input (1.6, 1.7).
"""

import os
from unittest.mock import MagicMock

import pytest

import mcc.web.file_utils
from mcc.checker.cf_shim import CF
from mcc.web.file_utils import get_dataset_from_file


@pytest.fixture(scope="session")
def data_dir():
    """
    Fixture that returns the absolute path of the test data directory
    """
    test_dir = os.path.dirname(os.path.realpath(__file__))
    yield os.path.join(test_dir, 'data')


def test_run_cf_checker(data_dir):
    """
    The test uses '§2.6 Attributes' netCDF standard from the resulting checker
    report to confirm that the selected CF version (1.6, 1.7) matches the
    checker that is run.
    """
    # get_dataset_from_file() utilizes Flask logging, so Mock the app instance out here
    mcc.web.file_utils.app = MagicMock()

    file = os.path.join(data_dir, 'tos_AMSRE_L3_v7_200206-201012.nc')

    with open(file, "rb") as infile:
        infile.filename = 'tos_AMSRE_L3_v7_200206-201012.nc'
        ds = get_dataset_from_file(infile)

    dataset = ds['dataset']

    cf = CF()

    # Setting CF checker to run NC file against 1.6 Conventions
    cf.setup('1.6')
    results = cf.run(dataset)
    print()  # Add a blank line so the report reads clearer when running this test suite from Pytest
    print('|--CF1.6--Checker Report--|')
    print(results)
    try:
        for keys in results:
            if keys == 'results':
                for keynames in results[keys]:
                    for attrkey in keynames['results']:
                        if attrkey['name'] == '§2.6 Attributes':
                            if ("CF-1.6" in attrkey['message']) or ("CF" not in attrkey['message']):
                                print('*********************************************')
                                print('******* Checker is CF Convention 1.6 ********')
                                print('*********************************************')
                                break

    except IndexError:
        print('Dataset Index Error')

    # Setting CF checker to run NC file against 1.6 Conventions
    cf.setup('1.7')
    results = cf.run(dataset)
    print('|--CF1.7--Checker Report--|')
    print(results)
    try:
        for keys in results:
            if keys == 'results':
                for keynames in results[keys]:
                    for attrkey in keynames['results']:
                        if attrkey['name'] == '§2.6 Attributes':
                            if ("CF-1.7" in attrkey['message']) or ("CF" not in attrkey['message']):
                                print('*********************************************')
                                print('******* Checker is CF Convention 1.7 ********')
                                print('*********************************************')
                                break

    except IndexError:
        print('Dataset Index Error')

    dataset.close()
