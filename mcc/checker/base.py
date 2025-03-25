"""
=======
base.py
=======

These classes form the base of the Checker.
The basic idea is to create Groupings of functions that correspond
to logical, natural groupings of the metadata specifications.

There are four distinct parts of this architecture.
(1) base Groups, Bluprints, Checkers, and Results that form a foundation
(2) checker functions that implement the Checker interface
(3) checksuites that implement and create blueprints
(4) the interface to parse the results (by default, the web interface)

So, to create a new test, we would...

1. Create a CheckSuite describing our group, with at a minimum, a constant
   instance level ABOUT dictionary and a setup() method that creates
   all the blueprints we will need for the test. In the setup() method is
   where we would configure different options for the test.
2. Add attributes / options to inherit on any group
3. Create Blueprints and bind Checkers to them to use the data contained in the
   blueprint.
4. Call run() on the checksuite to run all the tests and generate results
   objects
5. Interpret the results.

"""

import logging
import time
from collections import deque
from random import randrange

MANUALLY_DEFINED = 0
AUTO_FAIL = 1
RESULT_FAIL = 2
AUTO_PARTIAL = 3
AUTO_PASS = 4
RESULT_PASS = 5
"""Enumeration of result values from evaluation of a checker function."""

logger = logging.getLogger(__name__)


class Group(object):
    """
    A Group is a logical grouping of Blueprints/attributes.

    Attributes form the basis of what we use in the Group.
    This is influenced by the heavy usage of them in the netCDF4 python library.
    Important attributes trickle down groups into their Blueprints and Results,
    as long as they are not blacklisted.
    """
    # Don't extend the following from the CheckSuite, nor any blueprints/checkers
    EXTEND_BLACKLIST = frozenset(
        [
            'name', 'short_name', 'description', 'url', 'blueprints',
            'checkers', 'options',
        ]
    )

    # Don't extend down any blueprints or checkers, nor scope which is an
    # internal comment of sorts.
    RESULTS_BLACKLIST = frozenset(
        [
            'blueprints', 'checkers', 'scope'
        ]
    )

    @classmethod
    def group_results_scorer(cls, result_grouping):
        """
        Comparator function for final sorting.

          0    | manually defined grouping (do not sort)
          1    | automatic grouping that completely failed
          2    | Result that failed
          3    | automatic grouping that partially failed
          4    | automatic grouping that completely passed
          5    | Result that passed
        """
        score = MANUALLY_DEFINED

        if isinstance(result_grouping, dict):
            if 'automatic_grouping' in result_grouping:
                passed = result_grouping['passed']
                total = result_grouping['total']

                # All passed
                if passed == total:
                    score = AUTO_PASS
                # All failed
                elif passed == 0:
                    score = AUTO_FAIL
                # Partially passed
                else:
                    score = AUTO_PARTIAL
        elif isinstance(result_grouping, Result):
            score = RESULT_FAIL if not result_grouping.passed else RESULT_PASS

        return score

    def __init__(self, group_name, **kwargs):
        """
        Create a new Group.

        @param group_name how to describe the group (can be None)
        @param kwargs attributes to add...if checkers or blueprints aren't
                      specified then create empty deques
        """
        self.name = group_name

        for key, value in kwargs.items():
            setattr(self, key, value)

        if not hasattr(self, 'checkers'):
            self.checkers = deque()

        if not hasattr(self, 'blueprints'):
            self.blueprints = deque()

    def _get_extendable_attributes(self, new_checkers=None):
        """
        Get a copy of all the attributes set on this Group.

        @param new_checkers new Checker instances to add to the new attrs
        @return a dict of (key, value) pairs that contains all the information
                in the attributes of the Group, minus the EXTEND_BLACKLIST,
                but plus the checkers of the Group + and new_checkers
        """
        checkers = deque(self.checkers)

        if new_checkers:
            # Extend the new checkers on the right side so that we preserve
            # the correct ordering of tests (important for dependent tests).
            checkers.extend(new_checkers)

        keys = (key for key in list(vars(self).keys())
                if key not in Group.EXTEND_BLACKLIST)
        ret = {key: getattr(self, key) for key in keys}
        ret['checkers'] = checkers

        return ret

    def add_checker(self, function):
        """Appends a single checker function to this Group."""
        self.checkers.append(function)

    def add_checkers(self, *additional_checkers):
        """Extends the checkers within this Group with those provided."""
        self.checkers.extend(additional_checkers)

    def _add_blueprint(self, blueprint, attributes=None, *new_checkers):
        if attributes is None:
            attributes = self._get_extendable_attributes(new_checkers)

        blueprint = Blueprint(blueprint, **attributes)
        self.blueprints.append(blueprint)

    def add_blueprint(self, blueprint, *new_checkers):
        """Adds a new Blueprint (with optional additional checker functions) to this Group."""
        return self._add_blueprint(blueprint, None, *new_checkers)

    def add_blueprints(self, blueprints, *new_checkers):
        """Adds multiple Blueprint objects (with optional additional checker functions) to this Group."""
        attributes = self._get_extendable_attributes(new_checkers)

        for blueprint in blueprints:
            self._add_blueprint(blueprint, attributes=attributes)

    def add_group(self, group_name, **kwargs):
        """
        Add a new subgroup to this group.

        The results of the subgroup will be represented hierarchically within this
        Group and will be run automatically.

        @param group_name the name for the new group
        @param kwargs any attributes of this group to override/add
        @return the new Group instance
        """
        # Setup inheritance of attributes and checkers for subgroup.
        attributes = self._get_extendable_attributes()
        attributes.update(kwargs)
        attributes['checkers'] = deque(self.checkers)
        attributes['parent'] = self

        new_group = Group(group_name, **attributes)
        self.blueprints.append(new_group)

        return new_group

    def run(self, dataset):
        """
        Recursively performs a depth-first traversal and execution of subgroups
        and Blueprints. Performs summary scoring and moving forward of failed
        tests as the recursion completes.

        @param dataset a netCDF4 dataset to give to the blueprint execution
        @return a dict with non-blacklisted attributes of this group, summary
                scoring, a probably unique signed integer, and a list of results
        """
        total_number_passed = 0
        total_number_results = 0

        group_results = []

        for blueprint in self.blueprints:
            blueprint_results = blueprint.run(dataset)

            # This indicates that we are returning from a recursion.
            # That is, blueprint_results is a dict that is the result
            # of a Group.run() that was recursively present.
            if isinstance(blueprint_results, dict):
                total_number_passed += blueprint_results['passed']
                total_number_results += blueprint_results['total']
                group_results.append(blueprint_results)
            else:
                individual_results = []
                number_passed = 0
                number_total = 0

                for result in blueprint_results:
                    if result.passed:
                        number_passed += 1

                    number_total += 1
                    individual_results.append(result)
                    name = result.name

                if len(individual_results) <= 1:
                    group_results.extend(individual_results)
                else:
                    # Sort by passing status.
                    # Assertion: there should be no sublists
                    # Assertion: sorting algorithm is stable...
                    #            we want different checker results to maintain their adjacency...
                    # Python's default, mergesort, is stable
                    individual_results.sort(key=lambda result: result.passed)

                    results_bundle = {
                        'name': name,
                        'passed': number_passed,
                        'total': number_total,
                        'results': individual_results,
                        # TODO: hack (see note below)
                        'hash': hash(name) + randrange(1e5),
                        'automatic_grouping': True,
                        'priority': blueprint.priority if hasattr(blueprint, 'priority') else None,
                    }

                    group_results.append(results_bundle)

                total_number_passed += number_passed
                total_number_results += number_total

        group_results.sort(key=self.group_results_scorer)

        ret = {
            key: value for key, value in vars(self).items()
            if key not in Group.RESULTS_BLACKLIST
        }

        ret['results'] = group_results
        ret['passed'] = total_number_passed
        ret['total'] = total_number_results

        # Generate a pseudorandom hash for use in templates and unique naming
        # where there is no good method for uniquely referring to groups.
        # TODO: this is a hack and is only necessary for HTML
        ret['hash'] = hash(ret['name']) + randrange(1e5)

        return ret


class CheckSuite(Group):
    """
    A CheckSuite is the top-level grouping of a test.

    It is just a version of the Group class that has specific attributes that we
    check for below.

    In an implementation of a CheckSuite, one should define an ABOUT dict
    that contains (at a minimum), the keys in REQUIRED_KEYS.
    These are required for various UI elements and are good bookkeeping anyway.
    """
    REQUIRED_KEYS = ('name', 'short_name', 'description', 'url', 'versions')
    ABOUT = {}

    def __init__(self):
        missing_keys = [
            key for key in CheckSuite.REQUIRED_KEYS
            if key not in list(self.ABOUT.keys())
        ]

        if missing_keys:
            raise AttributeError(
                f'Suite must have kwargs ({", ".join(CheckSuite.REQUIRED_KEYS)}), missing ({", ".join(missing_keys)})'
            )

        # Initialize a Group with the validated attributes.
        super().__init__(None, **self.ABOUT)


class Blueprint(object):
    """
    A Blueprint describes the parameters, attributes, and Checkers that
    constitute a single check for something.

    A single Blueprint can map to multiple Checkers, and may be created
    directly with Python dicts as literals or parsed JSON, or may be created
    entirely programatically.
    """
    def __init__(self, blueprint=None, checkers=None, **kwargs):
        """
        In the case where the kwargs contain keys already covered
        by the blueprint, the kwarg values will be taken preferentially.

        @param blueprint dictionary of attributes to assign to this Blueprint object (can be None)
        @param checkers list of Checker class types (not instantiated objects) to assign to this Blueprint object
                        (can be None)
        @param kwargs additional attributes to assign to this Blueprint object
        """
        if blueprint is None:
            blueprint = {}

        self.checkers = checkers if checkers else tuple()

        blueprint.update(kwargs)
        for key, value in blueprint.items():
            setattr(self, key, value)

    @property
    def long_name(self):
        name_components = []
        parent = self.parent if hasattr(self, "parent") else None

        name_components.append(self.name)

        while parent is not None:
            name_components.append(parent.short_name if hasattr(parent, "short_name") else parent.name)
            parent = parent.parent if hasattr(parent, "parent") else None

        return ".".join(reversed(name_components))

    def run(self, dataset, indent=0):
        """
        Linearly run all the Checker instances assigned to this Blueprint.

        @param dataset a netCDF4 dataset
        @param indent an integer value indiciating the indentation level for logging
        """
        logger.debug(f"{'    ' * indent}Running blueprint \"{self.long_name}\" version {self.version}")

        for checker in self.checkers:
            checker_results_generator = checker(dataset).run(self, indent=indent+1)

            for result in checker_results_generator:
                yield result


class Checker(object):
    """
    The most complicated part of the base, the part that all other Classes
    revolve around.
    """
    # The name of the Checker object. This should almost always be redefined
    # by inheritors of this class to override this value with a specific name.
    CHECKER_NAME = "base checker"

    # The full netCDF4 dataset under investigation.
    dataset = None

    # [Optional] A piece of immutable data that can be pre-calculated.
    cached_data = None

    # The Blueprint object that the Checker is validating against.
    blueprint = None

    # Current value that the Checker is working with.
    # Used to easily pass the value to a Result object with convenience
    # methods without partial application of functions.
    current_value = None

    def __init__(self, dataset):
        """
        Each checker should call initialize() and do any other
        setup for instance variables it feels like.

        @param dataset a complete netCDF4 dataset
        """
        self.setup_dataset(dataset)

    def setup_dataset(self, dataset):
        if self.dataset is None:
            self.dataset = dataset

    def run(self, blueprint, indent=0):
        """
        Execute the Checker.

        If the Blueprint has a `scope` attribute, blueprint.name gets a special meaning:
            * globals: run the test against the global attribute given
            * varattrs: run the test against all variables for attribute
            * vars: run the test against global variables

        @param blueprint handle to the Blueprint object that invoked this Checker instance
        @param indent an integer value indiciating the indentation level for logging
        @return three-tuple of ([Result | list of Results],
                                number passed <int>,
                                number tested <int>)
        @raises NotImplementedError if scope is a non-standard value
        """
        logger.debug(f"{'  ' * indent}Running checker \"{self.CHECKER_NAME}\"")

        self.blueprint = blueprint

        start = time.time()

        scope = getattr(blueprint, 'scope', 'globals')

        if scope == 'globals':
            name = getattr(blueprint, 'name')
            value = getattr(self.dataset, name, None)
            self.current_value = value

            result = self.run_global(blueprint, value)
            yield result
        elif scope == 'varattrs':
            attribute = getattr(blueprint, 'name')

            for group in self.get_groups():
                # Choose variables to check (default to all)
                if hasattr(blueprint, 'variables'):
                    variables = {
                        name: group.variables.get(name, None)
                        for name in blueprint.variables
                    }
                else:
                    variables = group.variables

                for variable_name, variable in variables.items():
                    value = getattr(variable, attribute, None)
                    self.current_value = value

                    result = self.run_varattr(blueprint, variable_name, value)
                    yield result
        elif scope == 'vars':
            variable = getattr(blueprint, 'name')

            for group in self.get_groups():
                value = group.variables.get(variable)

                if value is not None:
                    representation = (f'{k}: "{v}"' for k, v in value.__dict__.items())
                    self.current_value = '; '.join(representation)
                else:
                    self.current_value = None

                result = self.run_vars(blueprint, value)
                yield result
        else:
            raise NotImplementedError(f'scope "{scope}" not implemented')

        end = time.time()

        logger.debug(f"{'  ' * indent}Checker \"{self.CHECKER_NAME}\" completed in {end - start:.3f} seconds")

    def get_groups(self):
        if self.dataset.groups:
            groups = [group for key, group in self.dataset.groups.items()]
        else:
            groups = [self.dataset]

        return groups

    def run_global(self, blueprint, value):
        """
        Use this method to test against a global attribute.

        Since this global check is often the easiest, it is most often
        convenient to write this method and have other run_* methods do
        setup and teardown, delegating actual checking to this method.

        @param blueprint an initialized Blueprint object
        @param value the value of the attribute being tested; if None,
                     the attribute might not exist
        @return a Result object with the result of the blueprint
        """
        raise NotImplementedError('must implement a run_global() method')

    def run_varattr(self, blueprint, variable, value):
        """
        Use this method to test against an attribute of all variables.

        This method can be easily overridden, but make sure to set the variable
        attribute of the result to the variable you're testing.

        @param blueprint an initialized Blueprint object
        @param variable the variable for which the attribute is referring to
        @param value the value of the attribute being tested; if None,
                     the attribute might not exist
        @return a Result object with the result of the blueprint for a single
                Variable
        """
        result = self.run_global(blueprint, value)
        setattr(result, 'variable', variable)
        return result

    def run_vars(self, blueprint, value):
        """
        Use this method to run a test against a Variable.
        This method can be easily overridden.

        @param blueprint an initialized Blueprint object
        @param value the Variable object being tested; if None, might not exist
        @return a Result object with the result of the blueprint
        """
        result = self.run_global(blueprint, value)
        return result

    def success(self, message, **kwargs):
        """Convenience method for easily creating a passing Result."""
        return Result(True, self.current_value, self.blueprint,
                      checker_name=self.CHECKER_NAME, message=message,
                      **kwargs)

    def error(self, message, **kwargs):
        """Convenience method for easily creating a failing Result."""
        return Result(False, self.current_value, self.blueprint,
                      checker_name=self.CHECKER_NAME, message=message,
                      **kwargs)


class Result(object):
    """
    A Result object is basically a dumb repository of attributes that
    we then parse out.
    """
    # Set of attribute names that are not carried over from a provided Blueprint.
    BLACKLIST = frozenset(['blueprints', 'checkers'])

    def __init__(self, passed, value, blueprint, **kwargs):
        """
        Create a new Result instance.

        @param passed a value such that bool(passed) is True if passed/warning
                      and bool(passed) is False if failure
        @param value the value (or lack thereof) of the blueprint's attempt
        @param blueprint a Blueprint instance
        @param kwargs additional attributes for the Result to hold onto
                      it is the responsility of the Results parser to deal
                      with these additional attributes
        """
        # Several possible values:
        #   True -> the Checker passed
        #   False -> the Checker did not pass
        #   None -> the Checker was not run
        #   <type 'str'> -> Checker was run, but Result is in a special category
        self.passed = passed
        self.value = value

        for attr, value in vars(blueprint).items():
            if attr not in Result.BLACKLIST:
                setattr(self, attr, value)

        # These optional values represent material for constructing user
        # feedback about the tests.
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<{0}>'.format(
            ', '.join(f'{k}: "{v}"' for k, v in vars(self).items())
        )

    def __str__(self):
        if hasattr(self, 'scope') and self.scope == 'varattrs':
            name = self.variable + ':' + self.name
        else:
            name = self.name

        if hasattr(self, 'priority') and self.priority == 'optional':
            return '{checker_name} of variable {name} {pass_str} {message}'.format(
                checker_name=self.checker_name,
                pass_str='is' if self.passed else 'is not',
                name=name,
                message=self.message
            ).rstrip()
        else:
            return '{checker_name} {pass_str} because "{name}" {message}'.format(
                checker_name=self.checker_name,
                pass_str='passed' if self.passed else 'failed',
                name=name,
                message=self.message
            ).rstrip()
