"""
=============
form_utils.py
=============

A set of utility functions for parsing GET and POST requests to run checkers.
"""

from flask import abort


def get_tests(form_dict, checker_map):
    """
    Initialize tests with (potential) parameter for running.

    @param form_dict ImmutableMultiDict from flask or a regular
                     dict that conforms to the format,
                     form_dict = ImmutableMultiDict([
                        ('GDS2-parameter', u'L2P'),
                        ('GDS2', u'on')])
    @param checker_map a dict of checker short names to initialized checkers
    @return a list of setup checkers that the user has selected
    """
    tests = []

    for short_name in checker_map:
        if short_name in form_dict:
            potential_parameter = form_dict.get(short_name + '-parameter')
            version_selection = form_dict.get(short_name + '-version')

            # Get an instance of the Checker
            checker = checker_map[short_name]()

            # Set up the tests with parameter if necessary
            if potential_parameter is not None and version_selection is not None:
                tests.append(checker.setup(potential_parameter, version_selection))
            elif potential_parameter is not None:
                tests.append(checker.setup(potential_parameter))
            elif version_selection is not None:
                tests.append(checker.setup(version_selection))
            else:
                tests.append(checker.setup(None))

    return tests


def parse_post_arguments(form_dict, files, checker_map):
    """
    Parse a POST request from either an HTML page form or a cURL-like request.
    Aborts response if no tests or no files.

    @param form_dict ImmutableMultiDict from flask or a regular
                     dict that conforms to the format,
                     form_dict = ImmutableMultiDict([
                        ('GDS2-parameter', u'L2P'),
                        ('GDS2', u'on')])
    @param files a dict with a flask file-like object
    @param checker_map a dict of checker short names to initialized checkers
    @return a dict with 'file', 'checkers', 'response' or abort()
    # TODO determine if this is an additional place to verify upload size constraint
    """
    ret = {}

    checkers = get_tests(form_dict, checker_map)

    if not checkers:
        return abort(
            400, "You need to choose at least one metadata convention to test your file against."
        )

    if 'file-upload' not in files:
        return abort(400, "Your request was empty. Please make sure you've specified a file.")
    elif not files['file-upload']:
        return abort(400, "There was a problem uploading your file. Please try again.")

    ret['file'] = files['file-upload']
    ret['checkers'] = checkers
    ret['response'] = form_dict.get('response', 'html').lower()

    return ret
