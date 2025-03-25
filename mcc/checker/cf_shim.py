
"""
==========
cf_shim.py
==========

Defines the CheckSuite and code patches for the Climate and Forcast (CF)
metadata conventions.

"""

import inspect
import logging
import sys
import time
from random import randrange

from compliance_checker import cfutil
from compliance_checker.base import BaseCheck, Result, fix_return_value
from compliance_checker.cf import util
from compliance_checker.cf.cf_1_6 import CF1_6Check
from compliance_checker.cf.cf_1_7 import CF1_7Check
from compliance_checker.cf.cf_base import CFNCCheck
from compliance_checker.suite import CheckSuite as CCCheckSuite
from flask import abort

from .base import CheckSuite

logger = logging.getLogger(__name__)


def remove_checks(checks, checker):
    """
    Remove unwanted checks from MCC report.

    Parameters
    ----------
    checks : list (bound CFNCCheck methods)
        List of bound CFNCheck methods that will be run as part of
        this report.
    checker : CFNCCheck
        CFNCCheck object the checks are bound to
    """
    checks_to_remove = [
        'check_variable_features',
        'check_all_features_are_same_type'
    ]

    for check in checks_to_remove:
        try:
            logger.debug(f'Removing check "{check}" from CF suite')
            index = checks.index(getattr(checker, check))
            del checks[index]
        except (ValueError, AttributeError):
            logger.debug(f'Check "{check}" not found, ignoring')


def _get_checks_patch(self, checkclass, include_checks, skip_checks):
    """
    Monkeypatch method for compliance_checker.CheckSuite._get_checks.

    Retreives check methods from a Checker class.  Excludes any checks in `skip_checks`.

    The name of the methods in the Checker class should start with "check_"
    for this method to find them.
    """
    meths = inspect.getmembers(checkclass, inspect.ismethod)

    # return all check methods not among the skipped checks
    return [x[1] for x in meths if x[0].startswith("check_") and
            x[0] not in skip_checks]


def group_run_patch(self, ds, skip_checks, *checker_names):
    """
    This is a Monkeypatch for compliance_checker.CheckSuite.run that adds group
    support to the CF Checker.
    """
    ret_val = {}
    include_dict = {}
    checkers = self._get_valid_checkers(ds, checker_names)

    if len(checkers) == 0:
        logger.warning("No valid checkers found for tests '%s'", ",".join(checker_names))

    for checker_name, checker_class in checkers:
        checker = checker_class()
        checker.setup(ds)

        checks = self._get_checks(checker, include_dict, skip_checks)
        vals = []
        errs = {}   # check method name -> (exc, traceback)

        remove_checks(checks, checker)

        if ds.groups:
            groups = [group for key, group in ds.groups.items()]
        else:
            groups = [ds]

        for group_idx, group in enumerate(groups):
            for check_idx, check in enumerate(checks):
                try:
                    logger.debug(f'Running check {check.__func__.__name__} {self.version} ({check_idx}) for group '
                                 f'{group_idx}')

                    start = time.time()
                    vals.extend(self._run_check(check, group))
                    end = time.time()

                    logger.debug(f'{check.__func__.__name__} {self.version} ({check_idx}) completed in '
                                 f'{end - start:.3f} seconds')
                except Exception as err:
                    logger.warning(f'{check.__func__.__name__} {self.version} ({check_idx}) failed to complete, '
                                   f'reason: {str(err)}')
                    errs[check.__func__.__name__] = (err, sys.exc_info()[2])

        groups = self.scores(vals)
        ret_val[checker_name] = groups, errs

    return ret_val


def _run_check_patch(self, check_method, ds):
    """
    Monkeypatch method for compliance_checker.CheckSuite._run_check.
    """
    val = check_method(ds)

    if isinstance(val, list):
        return [fix_return_value(v, check_method.__func__.__name__, check_method, check_method.__self__) for v in val]

    return [fix_return_value(val, check_method.__func__.__name__, check_method, check_method.__self__)]


def check_calendar_patch(self, ds):
    """
    Patched version of cf_1_6.CF1_6Check.check_calendar.

    The baseline version within compliance_checker contains a test that checks
    if an array of time values stratle the date 1582-10-15. Since this can
    be a computational bottleneck for datasets with long time arrays and
    is an irrelevant check for post-1970 satellite data, we substiute this
    version while removes said check. All other functionality of the original
    check_calendar method has been maintained.
    """
    standard_calendars = {
        "gregorian",
        "standard",
        "proleptic_gregorian",
        "noleap",
        "365_day",
        "all_leap",
        "366_day",
        "360_day",
        "julian",
        "none",
    }

    ret_val = []

    # this will only fetch variables with time units defined
    for time_var_name in cfutil.get_time_variables(ds):
        if time_var_name not in {var.name for var in util.find_coord_vars(ds)}:
            continue
        time_var = ds.variables[time_var_name]
        if not hasattr(time_var, "calendar"):
            continue
        if time_var.calendar.lower() == "gregorian":
            reasoning = (
                f"For time variable {time_var.name}, when using "
                "the standard Gregorian calendar, the value "
                '"standard" is preferred over "gregorian" for '
                "the calendar attribute"
            )
            result = Result(
                BaseCheck.LOW,
                False,
                self.section_titles["4.4.1"],
                [reasoning],
            )
            ret_val.append(result)
        # if a nonstandard calendar, then leap_years and leap_months must
        # be present
        if time_var.calendar.lower() not in standard_calendars:
            result = self._check_leap_time(time_var)
        # passes if the calendar is valid, otherwise notify of invalid
        # calendar
        else:
            result = Result(BaseCheck.LOW, True, self.section_titles["4.4.1"])
        ret_val.append(result)

    return ret_val


# CF 1.6 Conventions
class CF1_6Shim(CCCheckSuite):
    CF1_6Check.check_calendar = check_calendar_patch
    checkers = {'cf': CF1_6Check}
    _get_checks = _get_checks_patch
    _run_check = _run_check_patch
    run = group_run_patch
    version = '1.6'


# CF 1.7 Conventions
class CF1_7Shim(CCCheckSuite):
    CF1_7Check.check_calendar = check_calendar_patch
    checkers = {'cf': CF1_7Check}
    _get_checks = _get_checks_patch
    _run_check = _run_check_patch
    run = group_run_patch
    version = '1.7'


class CF(CheckSuite):
    ABOUT = {
        'name': 'netCDF Climate and Forecast Metadata Conventions',
        'short_name': 'CF',
        'url': 'http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html',
        'versions': ('1.6', '1.7'),
        'description': 'The conventions define metadata that provide a definitive description of what the data in '
                       'each variable represents, and the spatial and temporal properties of the data. This enables '
                       'users of data from different sources to decide which quantities are comparable, and '
                       'facilitates building applications with powerful extraction, regridding, and display '
                       'capabilities. The CF conventions generalize and extend the COARDS conventions.',
    }

    DEFAULT_VERSION = '1.6'

    def _parse_node(self, parent):
        ret = {
            'name': parent.name,
            'passed': parent.value[0],
            'total': parent.value[1],
        }

        if parent.msgs:
            try:
                ret['message'] = '\n'.join(parent.msgs)
            except TypeError:
                ret['message'] = parent.msgs

        if parent.children:
            ret['results'] = [self._parse_node(x) for x in parent.children]

        ret['hash'] = hash(ret['name']) + randrange(1e5)

        return ret

    def _reduce_score(self, node_list):
        # take advantage of the fact that the top-level scores have
        # already summed their children
        passed, total = 0, 0

        for x in node_list:
            passed += x['passed']
            total += x['total']

        return passed, total

    def run(self, dataset):
        results = []

        try:
            results = self.shim.run(dataset, 'cf')['cf'][0]
        except KeyError as err:
            logger.warning(f"The key {str(err)} does not exist")

        results = [self._parse_node(node) for node in results]
        total_passed, total = self._reduce_score(results)

        ret = {k: v for k, v, in CF.ABOUT.items()}
        ret['results'] = [
            {
                'name': 'Compliance Checker',
                'passed': total_passed,
                'total': total,
                'results': results,
            }
        ]
        ret['passed'] = total_passed
        ret['total'] = total

        return ret

    def setup(self, version):
        # Selected version value from CF dropdown toggle executes respective version run method
        if version not in CF.ABOUT['versions']:
            return abort(
                400, f'Must specify version in the format "CF-version=x.x". '
                     f'Available versions are {str(CF.ABOUT["versions"])}'
            )

        self.version = version

        if version == '1.6':
            self.shim = CF1_6Shim()
        elif version == '1.7':
            self.shim = CF1_7Shim()

        return self
