
"""
===========
checkers.py
===========

Definitions of all Checker implementations.

See the definition of Checker in base.py for more information on which methods
need to be implemented and to what extent for new Checkers.

"""

import json
import logging
import re
from difflib import get_close_matches
from os.path import dirname, join

import numpy as np
from cf_units import Unit
from isodate import parse_date, parse_datetime, parse_duration

from .base import Checker

logger = logging.getLogger(__name__)


class CheckExistence(Checker):
    """
    Checks if value is valid, which implies the existence of the value.
    This Checker is tightly coupled with the value passing in base.py
    """
    USELESS_VALUES = ('null', 'NULL', 'none', 'NONE', 'NIL', 'nil', '', 'n/a', 'N\A',)
    CHECKER_NAME = 'check for existence'

    def run_global(self, blueprint, value):
        if value is None:
            return self.error('does not exist')
        elif isinstance(value, str) and value in CheckExistence.USELESS_VALUES:
            return self.error(f'exists, but value "{value}" is not useful')

        return self.success('exists')

    def run_vars(self, blueprint, value):
        result = self.run_global(blueprint, value)
        setattr(result, 'value', None)

        return result


class CheckCommaSeparated(Checker):
    """
    Determines if a value is comma-separated or not based on a simple majority
    count of comma characters versus non-{alphanumeric,comma,space} characters.
    """
    # note this character set is not unicode aware
    NON_ALPHANUMERIC = re.compile(r'[^A-z0-9 ,]')
    CHECKER_NAME = 'check for a comma separated value'

    @staticmethod
    def commas_dominant(value):
        """
        Heuristically see if commas are the dominant non-alphanumeric character
        (over e.g. spaces, slashes, semicolons, etc.)

        @param value a string (assume so)
        @return three-tuple where (commas dominant <bool>,
                                   number commas <int>,
                                   number of other symbols per regex <int>)
        """
        number_commas = sum(1 for character in value if character == ',')

        number_nonalphanumeric = sum(
            1 for char in CheckCommaSeparated.NON_ALPHANUMERIC.finditer(value)
        )

        is_majority_commas = number_commas > number_nonalphanumeric

        return is_majority_commas, number_commas, number_nonalphanumeric

    def run_global(self, blueprint, value):
        if value is None:
            return self.error('does not exist')

        dominant, _, _ = CheckCommaSeparated.commas_dominant(value)

        if dominant:
            return self.success('is separated by commas')

        return self.error('might not be comma separated')


class CheckStandardName(Checker):
    """
    Determines whether a value is in a version of the standard name table.

    The json file used is generated from xml files of standard names
    (see mcc/utils/standard_names_converter.py).

    If we can't find an exact match of the standard name, then fail but provide
    a suggestion if one is found. This process is very slow (relatively), so
    use this with caution.
    """
    STANDARD_NAME_TABLE_FN = join(dirname(__file__), 'data', 'CF-Standard-Names-Table-77.json')
    CHECKER_NAME = 'check for standard name'

    def __init__(self, dataset):
        super().__init__(dataset)

        if not self.cached_data:
            with open(self.STANDARD_NAME_TABLE_FN) as infile:
                self.cached_data = json.load(infile)
                self.cached_keys = list(self.cached_data['data'].keys())

    def run_global(self, blueprint, value):
        if value is None:
            return self.error('does not exist')

        name_in_table = value in self.cached_keys

        if name_in_table:
            return self.success(f'has value in {value} standard name table')

        best_guess_standard_name = get_close_matches(value, self.cached_keys, 1)

        if best_guess_standard_name:
            message = (f'has invalid standard name (v{self.cached_data["version"]}). '
                       f'best guess: {best_guess_standard_name[0]}')
        else:
            message = f'has invalid standard name (v{self.cached_data["version"]})'

        return self.error(message)


class CheckUDUnits(Checker):
    """
    Determines if a value is a valid UD Unit.

    The heavy lifting is done by udunitspy.
    """
    CHECKER_NAME = 'check for valid UD Unit'

    def run_global(self, blueprint, value):
        if value is None:
            return self.error('does not exist')

        message = 'has {message} unit "{u}"'
        unit_string = str(value)

        try:
            # if type(unit_string) is unicode, this causes cf_units to fail...
            unit = Unit(unit_string)

            return self.success(message.format(u=str(unit), message='valid'))
        except (ValueError, TypeError) as err:
            logger.warning(f"UNKNOWN unit: %s not recognized by UDUNITS, reason: %s", unit_string, str(err))
            return self.error(message.format(u=value, message='invalid'))


class CheckPossibleValues(Checker):
    """
    Checks value against a list of `possible_values` which should be an
    attribute of the check.
    """
    CHECKER_NAME = 'check for value in a set of possible values'

    def run_global(self, blueprint, value):
        if value is None:
            return self.error('does not exist')

        possible_values = blueprint.possible_values

        if value in possible_values:
            return self.success(f'has value "{value}", which is in list of possible values')

        message = (f'value "{value}" not in list of possible values... '
                   f'allowed values are ({", ".join(possible_values)})')

        return self.error(message)


class CheckISODatestuff(Checker):
    """
    Validates ISO-8601 datetimes, falling back to dates if that doesn't work.
    """
    CHECKER_NAME = 'check for valid iso-8601 date(time)'

    def run_global(self, blueprint, value):
        if value is None:
            return self.error('does not exist')

        # Try to parse out datetime
        try:
            parse_datetime(value)
            return self.success('has a valid ISO-8601 datetime')
        except ValueError:
            pass

        # If that doesn't work, try to parse out a date
        try:
            parse_date(value)
            return self.success('has a valid ISO-8601 date (but not datetime)')
        except ValueError:
            pass

        return self.error('is not a valid date or datetime')


class CheckISODuration(Checker):
    """
    Validates ISO-8601 durations.
    """
    CHECKER_NAME = 'check for valid iso-8601 duration'

    def run_global(self, blueprint, value):
        if value is None:
            return self.error('does not exist')

        try:
            parse_duration(value)
            return self.success('is a valid duration')
        except (ValueError, TypeError):
            pass

        return self.error('is not a valid duration')


class CheckDeprecated(Checker):
    """
    Reverses validation for deprecated elements.
    """
    CHECKER_NAME = 'check for deprecated elements'

    def run_global(self, check, value):
        if value is not None:
            return self.error('Deprecated Attribute')
        else:
            return self.success('does not exist')


class CheckTypes(Checker):
    """
    Checks if a value matches one (or more) valid types for the value.

    The check is expected to have an attribute `type` which is either a string,
    a tuple of type strings, or a list of type strings.

    The valid type strings are {byte, short, int, lomg, string, float, double}.
    The mapping of these types to values is taken from the GDS2 manual,
    GDSR20r5.pdf, page 17.
    """
    TYPE_MAP = {
        'byte': np.int8,
        'short': np.int16,
        'int': np.int32,
        'long': np.int32,
        'string': str,
        'float': np.float32,
        'double': np.float64,
    }

    REVERSE_TYPE_MAP = {
        np_type.__name__: human_name
        for (human_name, np_type) in TYPE_MAP.items()
    }

    CHECKER_NAME = 'check for valid numpy types'

    @classmethod
    def equal_types(cls, have_type, want_type):
        """
        Determine type equality using np.issubdtype().

        @param have_type a type object that represents the current type we have
        @param want_type a type object that represents what have_type
                         should be less than or equal to on the type hierarchy
        @return a three-tuple of (np.issubdtype(have_type, want_type) <bool>,
                                  have_type human-readable <str>,
                                  want_type human-readable <str>)
        """
        type_is_leq = np.issubdtype(have_type, want_type)

        have_type_name = have_type.__name__ if not isinstance(have_type, np.dtype) else str(have_type)
        have_type_name = cls.REVERSE_TYPE_MAP.get(have_type_name, have_type_name)
        want_type_name = cls.REVERSE_TYPE_MAP[want_type.__name__]

        return type_is_leq, have_type_name, want_type_name

    def run_global(self, blueprint, value, have_type=None):
        if value is None:
            return self.error('does not exist')
        elif have_type is None:
            have_type = type(value)

        # Set to None so we can hide on display
        setattr(self, 'current_value', None)

        if isinstance(blueprint.type, (tuple, list)):
            for type_string in blueprint.type:
                want_type = self.TYPE_MAP[type_string]
                passed, have_type_name, want_type_name = self.equal_types(have_type, want_type)

                if passed:
                    return self.success(f'has type {have_type_name}')
            else:
                message = f'has type {have_type_name} not in {", ".join(blueprint.type)}'
                return self.error(message)
        else:
            want_type = self.TYPE_MAP[blueprint.type]
            passed, have_type_name, want_type_name = self.equal_types(have_type, want_type)

            if passed:
                return self.success(f'has type {have_type_name}')

            message = f'has type {have_type_name} when we want type {want_type_name}'

            return self.error(message)

    def run_vars(self, blueprint, value):
        if not value:
            return self.error('does not exist')

        result = self.run_global(blueprint, value, have_type=value.datatype)
        return result
