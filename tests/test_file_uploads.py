
"""
====================
test_file_uploads.py
====================

Testing File Uploads for the (4/10) UAT test cases:
https://wiki.jpl.nasa.gov/display/PD/MCC+v1.4+UAT+Test+Cases

Several NC files are run through ALL 3 Checkers (ACDD, CF, GDS2) and their
respective checker versions.

"""

import logging
import os
import time

import netCDF4 as nc
import pytest

from mcc.checker.acdd import ACDD
from mcc.checker.cf_shim import CF
from mcc.checker.gds2 import GDS2

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def data_dir():
    """
    Fixture that returns the absolute path of the test data directory
    """
    test_dir = os.path.dirname(os.path.realpath(__file__))
    yield os.path.join(test_dir, 'data')


def test_file_uploads(data_dir):
    test_files = [
        'ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc',
        'S6A_P4_2__LR_RED__NR_022_215_20210622T065556_20210622T085149_F02.nc',
        'IS2SITMOGR4_01_201912_004_001.nc'
    ]

    for file_name in test_files:
        dataset = nc.Dataset(os.path.join(data_dir, file_name))

        # Test File with ACDD Checker
        results_ACDD = run_file_ACDD(file_name, dataset)
        assert results_ACDD == "Passed"

        # Test File with CF Checker
        results_CF = run_file_CF(file_name, dataset)
        assert results_CF == "Passed"

        # Test File with GDS2 Checker
        results_GDS2 = run_file_GDS2(file_name, dataset)
        assert results_GDS2 == "Passed"

        dataset.close()


def run_file_ACDD(file_name, dataset):
    acdd = ACDD()

    for acdd_version in ('1.1', '1.3'):
        acdd.setup(acdd_version)
        logger.info(f"Running {file_name} against ACDD v{acdd_version}")
        start = time.time()
        result = acdd.run(dataset)
        end = time.time()
        logger.info(f"{file_name} passed {result['passed']} tests out of {result['total']} in {end - start:.3f} seconds")

    return "Passed"


def run_file_CF(file_name, dataset):
    cf = CF()

    for cf_version in ('1.6', '1.7'):
        cf.setup(cf_version)
        logger.info(f"Running {file_name} against CF v{cf_version}")
        start = time.time()
        result = cf.run(dataset)
        end = time.time()
        logger.info(f"{file_name} passed {result['passed']} tests out of {result['total']} in {end - start:.3f} seconds")

    return "Passed"


def run_file_GDS2(file_name, dataset):
    gds2 = GDS2()

    for gds2_version in ('L2P', 'L3', 'L4'):
        gds2.setup(gds2_version)
        logger.info(f"Running {file_name} against GDS2 {gds2_version}")
        start = time.time()
        result = gds2.run(dataset)
        end = time.time()
        logger.info(f"{file_name} passed {result['passed']} tests out of {result['total']} in {end - start:.3f} seconds")

    return "Passed"
