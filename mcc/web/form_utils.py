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
    Optimized for handling large files (4GB+) efficiently.
    Aborts response if no tests or no files.

    @param form_dict ImmutableMultiDict from flask or a regular
                     dict that conforms to the format,
                     form_dict = ImmutableMultiDict([
                        ('GDS2-parameter', u'L2P'),
                        ('GDS2', u'on')])
    @param files a dict with a flask file-like object
    @param checker_map a dict of checker short names to initialized checkers
    @return a dict with 'file', 'checkers', 'response' or abort()
    """
    from flask import current_app
    app = current_app
    
    ret = {}

    # Get the selected checkers
    checkers = get_tests(form_dict, checker_map)

    if not checkers:
        return abort(
            400, "You need to choose at least one metadata convention to test your file against."
        )

    # Check for file upload
    # Try multiple possible field names for file uploads
    uploaded_file = None
    for field in ['file-upload', 'file', 'upload', 'fileUpload']:
        if field in files and files[field]:
            uploaded_file = files[field]
            app.logger.info(f"Found file in field: {field}")
            break
    
    if not uploaded_file:
        return abort(400, "Your request was empty. Please make sure you've specified a file.")
    
    # Log file information
    app.logger.info(f"File received: {uploaded_file.filename}")
    
    # Return the file object directly - we'll handle streaming in get_dataset_from_file
    ret['file'] = uploaded_file
    ret['checkers'] = checkers
    ret['response'] = form_dict.get('response', 'html').lower()

    return ret
