#!/usr/bin/env python

# Main .wsgi script for the program.
# From http://flask.pocoo.org/docs/deploying/mod_wsgi/

import os
import sys
import tempfile

sys.path.append(os.path.dirname(__file__))


def application(environ, start_response):
    # Increased API file size limit to 5GB (5 * 1024^3 = 5,368,709,120 bytes)
    os.environ['ApiMaxFileSize'] = environ.get('ApiMaxFileSize', '5368709120')
    # Increased UI file size limit to 5GB (5 * 1024^3 = 5,368,709,120 bytes)
    os.environ['UiMaxFileSize'] = environ.get('UiMaxFileSize', '5368709120')
    os.environ['HomepageURL'] = environ.get('HomepageURL', '"https://mcc.podaac.earthdatacloud.nasa.gov"')
    # Use /tmp for temporary file storage to ensure enough space for 4GB+ files
    os.environ['TempFileLocation'] = environ.get('TempFileLocation', '/tmp')
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
