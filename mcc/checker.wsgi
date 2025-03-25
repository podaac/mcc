#!/usr/bin/env python

# Main .wsgi script for the program.
# From http://flask.pocoo.org/docs/deploying/mod_wsgi/

import os
import sys

sys.path.append(os.path.dirname(__file__))


def application(environ, start_response):
	os.environ['MaxFileSize'] = environ.get('MaxFileSize', '')
	os.environ['HomepageURL'] = environ.get('HomepageURL', '')
	os.environ['TempFileLocation'] = environ.get('TempFileLocation', '')
	os.environ['Venue'] = environ.get('Venue', 'OPS')
	from web.server import app as _application

	return _application(environ, start_response)
