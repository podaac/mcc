"""
================
test_checkers.py
================

Unit tests for the custom Checker classes in checkers.py
"""

import os
import pytest

from netCDF4 import Dataset

from mcc.checker.base import Blueprint, Result
from mcc.checker.checkers import (CheckExistence,
                                  CheckCommaSeparated,
                                  CheckStandardName,
                                  CheckUDUnits,
                                  CheckPossibleValues,
                                  CheckISODatestuff,
                                  CheckISODuration,
                                  CheckDeprecated,
                                  CheckTypes)

@pytest.fixture(scope="session")
def test_granule():
    """Fixture that returns a sample granule as a NetCDF Dataset"""
    test_dir = os.path.dirname(os.path.realpath(__file__))
    granlue_path = os.path.join(test_dir, 'data', 'ascat_20210101_000900_metopa_73696_eps_o_coa_3202_ovw.l2.nc')
    yield Dataset(granlue_path, 'r')

def test_check_existence(test_granule):
    """Unit tests for checkers.CheckExistence"""
    blueprint = Blueprint(blueprint={'name': 'title', 'description': 'A short description of the dataset.'})
    checker = CheckExistence(test_granule)
    checker.blueprint = blueprint

    result = checker.run_vars(blueprint, value=None)
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

    result = checker.run_vars(blueprint, value='NULL')
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'exists, but value "NULL" is not useful'

    result = checker.run_vars(blueprint, value='Title')
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'exists'

def test_check_comma_separated(test_granule):
    """Unit tests for checkers.CheckCommaSeparated"""
    blueprint = Blueprint(blueprint={'name': 'keywords', 'description': 'A comma separated list of key words and phrases'})
    checker = CheckCommaSeparated(test_granule)
    checker.blueprint = blueprint

    result = checker.run_global(blueprint, value=None)
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

    result = checker.run_global(blueprint, value="Not/a/comma/separated/string")
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'might not be comma separated'

    result = checker.run_global(blueprint, value="SingleStringValue")
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'is separated by commas'

    result = checker.run_global(blueprint, value="a,comma , separated,string")
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'is separated by commas'

    result = checker.run_global(blueprint, value="comma<,separated>,with/,extra-,characters.,,")
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'is separated by commas'

def test_check_standard_name(test_granule):
    """Unit tests for checkers.CheckStandardName"""
    blueprint = Blueprint(blueprint={
        'name': 'standard_name',
        'description': 'A long descriptive name for the variable taken from a '
                       'controlled vocabulary of variable names.'}
    )
    checker = CheckStandardName(test_granule)
    checker.blueprint = blueprint

    result = checker.run_global(blueprint, value="age_of_sea_ice")
    assert isinstance(result, Result)
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has value in age_of_sea_ice standard name table'

    result = checker.run_global(blueprint, value="age_of_see_ice")
    assert not result.passed
    assert hasattr(result, 'message')
    assert 'has invalid standard name' in result.message
    assert 'best guess: age_of_sea_ice' in result.message

    result = checker.run_global(blueprint, value="not_a_standard_name")
    assert not result.passed
    assert hasattr(result, 'message')
    assert 'has invalid standard name' in result.message
    assert 'best guess' not in result.message

def test_check_udunits(test_granule):
    """Unit tests for checkers.CheckUDUnits"""
    blueprint = Blueprint(blueprint={
        'name': 'units',
        'description': 'The units of the variables data values. This attributes\' '
                       'value should be a valid udunits string.'}
    )
    checker = CheckUDUnits(test_granule)
    checker.blueprint = blueprint

    result = checker.run_global(blueprint, value=None)
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

    result = checker.run_global(blueprint, value='volts')
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has valid unit "volts"'

    result = checker.run_global(blueprint, value='dB')
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has invalid unit "dB"'

def test_check_possible_values(test_granule):
    """Unit tests for checkers.CheckPossibleValues"""
    blueprint = Blueprint(blueprint={
        'name': 'cdm_data_type',
        'possible_values': ['vector', 'grid', 'textTable', 'tin', 'stereoModel', 'video'],
        'description': 'The THREDDS data type appropriate for this dataset'}
    )
    checker = CheckPossibleValues(test_granule)
    checker.blueprint = blueprint

    result = checker.run_global(blueprint, value=None)
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

    result = checker.run_global(blueprint, value='video')
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has value "video", which is in list of possible values'

    result = checker.run_global(blueprint, value='radio')
    assert not result.passed
    assert hasattr(result, 'message')
    assert 'value "radio" not in list of possible values... ' in result.message

def test_check_iso_date_stuff(test_granule):
    """Unit tests for checkers.CheckISODatestuff"""
    blueprint = Blueprint(blueprint={
        'name': 'date_created',
        'description': 'The date on which the data was created.'}
    )
    checker = CheckISODatestuff(test_granule)
    checker.blueprint = blueprint

    result = checker.run_global(blueprint, value=None)
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

    result = checker.run_global(blueprint, value="2025-04-08T10:30:00.000Z")
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has a valid ISO-8601 datetime'

    result = checker.run_global(blueprint, value='2025-04-08')
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has a valid ISO-8601 date (but not datetime)'

    result = checker.run_global(blueprint, value='not a date or datetime')
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'is not a valid date or datetime'

def test_check_iso_duration(test_granule):
    """Unit tests for checkers.CheckISODuration"""
    blueprint = Blueprint(blueprint={
        'name': 'time_coverage_duration',
        'description': 'Describes the temporal coverage of the data as a time range.'}
    )
    checker = CheckISODuration(test_granule)
    checker.blueprint = blueprint

    result = checker.run_global(blueprint, value=None)
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

    result = checker.run_global(blueprint, value="P3Y6M4DT12H30M5S")
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'is a valid duration'

    result = checker.run_global(blueprint, value='not a valid duration')
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'is not a valid duration'

def test_check_deprecated(test_granule):
    """Unit tests for checkers.CheckDeprecated"""
    blueprint = Blueprint(blueprint={
        'name': 'Metadata_Convention',
        'description': "removed in favor of 'Conventions'"}
    )
    checker = CheckDeprecated(test_granule)
    checker.blueprint = blueprint

    result = checker.run_global(blueprint, value="Not None")
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'Deprecated Attribute'

    result = checker.run_global(blueprint, value=None)
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

def test_check_types(test_granule):
    """Unit tests for checkers.CheckTypes"""
    blueprint = Blueprint(blueprint={
        'name': 'Value',
        'description': 'Description',
        'type': ['int']}
    )
    checker = CheckTypes(test_granule)
    checker.blueprint = blueprint

    result = checker.run_vars(blueprint, value=None)
    assert isinstance(result, Result)
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'does not exist'

    result = checker.run_vars(blueprint, value=test_granule.variables['time'])
    assert result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has type long'

    result = checker.run_vars(blueprint, value=test_granule.variables['ice_age'])
    assert not result.passed
    assert hasattr(result, 'message')
    assert result.message == 'has type short not in int'
