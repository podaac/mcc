#!/usr/bin/env python
from web.server import app

"""
Dev server for the web app. Do not run this in production. Instead use the
WSGI interface.
"""


if __name__ == '__main__':
    # This line will print twice initially as a result of having auto reload
    # enabled. Disable with app.run(auto_reload=False, ...).
    print('***** DEBUG SERVER. DO NOT RUN THIS IN PRODUCTION *****')
    print('Running app on localhost:8999')
    app.run(debug=True, port=8999)
