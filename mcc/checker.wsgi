#!/usr/bin/env python

# Main .wsgi script for the program.
# From http://flask.pocoo.org/docs/deploying/mod_wsgi/

import os
import sys
import tempfile

sys.path.append(os.path.dirname(__file__))


def application(environ, start_response):
    os.environ['MaxFileSize'] = environ.get('MaxFileSize', '4295000000')
    os.environ['HomepageURL'] = environ.get('HomepageURL', '"https://mcc.podaac.earthdatacloud.nasa.gov"')
    os.environ['TempFileLocation'] = environ.get('TempFileLocation', tempfile.gettempdir())
    os.environ['Venue'] = environ.get('Venue', 'OPS')
    os.environ['CF_STANDARD_NAME_TABLE'] = environ.get('CF_STANDARD_NAME_TABLE', '')

    # Need to import only after all envvars have been populated
    from web.server import app as _application

    if os.environ['CF_STANDARD_NAME_TABLE'] and not os.path.exists(os.environ['CF_STANDARD_NAME_TABLE']):
        _application.logger.warning(
            f'Custom Standard Names Table "{os.environ["CF_STANDARD_NAME_TABLE"]}" does not exist. '
            f'The default table bundled with the CF Suite will be used instead.'
        )
    else:
        _application.logger.info(f'Using custom Standard Names Table {os.environ["CF_STANDARD_NAME_TABLE"]}')

    return _application(environ, start_response)
