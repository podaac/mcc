"""
=========
server.py
=========

Flask server front end for the MCC service.

"""

import time
from os import environ
from os.path import join

import pdfkit
from flask import Flask, render_template, request, abort, jsonify, make_response

from checker.acdd import ACDD
from checker.cf_shim import CF
from checker.gds2 import GDS2
from .file_utils import format_byte_size, get_dataset_from_file
from .form_utils import parse_post_arguments
from .json_utils import CustomJSONEncoder

app = Flask(__name__)

# Style options for whitespace in templated HTML code.
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# The JSON encoder in use when we call flask.jsonify()
app.json_encoder = CustomJSONEncoder

# Maximum allowed file size. Typically defaults to 2-4GB.
app.config['MAX_CONTENT_LENGTH'] = int(environ['MaxFileSize'])

# URL to use for MCC homepage.
app.config['HomepageURL'] = environ['HomepageURL']

# Venue that MCC is deployed to (SIT, UAT, or OPS)
app.config['Venue'] = str(environ['Venue'])

# Mapping of checker short names to CheckSuite implementations.
# This could be easily kept up-to-date by inspection of a module, but
# prefer the explicit writing of current checkers.
CHECKERS = {
    ACDD.ABOUT['short_name']: ACDD,
    CF.ABOUT['short_name']: CF,
    GDS2.ABOUT['short_name']: GDS2,
}

# MCC version - from VERSION file
with open('/var/www/html/mcc/web/VERSION', 'r') as f:
    version_file = f.read().rstrip()
    mcc_version = version_file


# Error handlers for select HTTP Response Codes.
# The rest are the default. Note, these may be overridden if an error occurs in
# Apache, e.g. if file size is too big then Python won't throw an error, but
# Apache will instead, meaning the page will not be styled or templated.
@app.errorhandler(413)
def req_entity_too_large(err):
    if request.form.get('response') in ('html', 'pdf'):
        ret = render_template(
            'error.html',
            error='File upload too large',
            text="",
            description=f"The maximum upload size is {format_byte_size(app.config['MAX_CONTENT_LENGTH'])}.",
            homepage_url=app.config['HomepageURL']
        )
        return ret, 413
    # Default to JSON-format response
    else:
        ret = {
            'error': 'File upload too large',
            'text': '',
            'description': f"The maximum upload size is {format_byte_size(app.config['MAX_CONTENT_LENGTH'])}."
        }
        return jsonify(ret), 413


@app.errorhandler(500)
def internal_server_error(err):
    if request.form.get('response') in ('html', 'pdf'):
        ret = render_template(
            'error.html',
            error='Unable to read file',
            text="",
            description=err.description,
            homepage_url=app.config['HomepageURL']
        )
        return ret, 500
    # Default to JSON-format response
    else:
        ret = {
            'error': 'Unable to read file',
            'text': '',
            'description': err.description
        }
        return jsonify(ret), 500


@app.errorhandler(404)
def page_not_found(err):
    if request.form.get('response') in ('html', 'pdf'):
        ret = render_template(
            'error.html',
            error='404 Page Not Found',
            text='Could not find page',
            description=err.description,
            homepage_url=app.config['HomepageURL']
        )
        return ret, 404
    # Default to JSON-format response
    else:
        ret = {
            'error': '404 Page Not Found',
            'text': 'Could not find page',
            'description': err.description
        }
        return jsonify(ret), 404


@app.errorhandler(400)
def bad_request(err):
    if request.form.get('response') in ('html', 'pdf'):
        ret = render_template(
            'error.html',
            error='There was a problem with your request',
            text='',
            description=err.description,
            homepage_url=app.config['HomepageURL']
        )
        return ret, 400
    else:
        ret = {
            'error': 'There was a problem with your request',
            'text': '',
            'description': err.description
        }
        return jsonify(ret), 400


# App endpoint implementations
@app.route('/check', methods=['POST'])
def check():
    """
    Takes a request with a completed form, performs the upload, and attempts
    to run the requested tests.

    @return rendered template of results or an error page if not form properly
            filled out with values / proper datasets
    """
    request_dict = request.form

    app.logger.info("UPLOAD REQUEST: %s", request.form)
    app.logger.info("FILE: %s", request.files.get('file-upload'))

    if 'response' not in request_dict:
        return abort(
            400, 'You need to include "response" in the request body and '
                 'assign the desired response type ("html", "json", or "pdf").'
        )

    selected_checkers = {}

    if request_dict.get('ACDD') == 'on':
        selected_checkers['ACDD-version'] = request_dict.get('ACDD-version') or ACDD.DEFAULT_VERSION

    if request_dict.get('CF') == 'on':
        selected_checkers['CF-version'] = request_dict.get('CF-version') or CF.DEFAULT_VERSION

    if request_dict.get('GDS2') == 'on':
        selected_checkers['GDS2-parameter'] = request_dict.get('GDS2-parameter') or GDS2.DEFAULT_VERSION

    info = parse_post_arguments(request.form, request.files, CHECKERS)
    app.logger.info("PARSED POST ARGUMENTS: %s", info)

    # read data in from the open file handle
    ds = get_dataset_from_file(info['file'])

    # this is only used for the output report
    ds_data_model = ds['dataset'].data_model

    # For all the selected checker objects, run their run() method on the dataset,
    # as processed by NETCDF4
    checkers = info['checkers']
    results = []

    for checker in checkers:
        app.logger.info("Running Checker %s (%s)", checker.name, checker.version)

        start = time.time()
        results.append(checker.run(ds['dataset']))
        end = time.time()

        app.logger.info(
            "Checker %s (%s) completed in %.3f seconds", checker.name, checker.version, end - start
        )

    # Formulate the response payload
    with ds['dataset']:  # ensure the NetCDF4 Dataset is closed once we're done here
        if info['response'] == 'json':
            response = jsonify(
                {
                    'mcc_version': mcc_version,
                    'selected_checkers': selected_checkers,
                    'fn': ds['filename'],
                    'md5': ds['hash'],
                    'size': ds['size'],
                    'model': ds_data_model,
                    'results': results,
                }
            )
        elif info['response'] == 'html':
            response = render_template(
                'results.html',
                selected_checkers=selected_checkers,
                results=results,
                fn=ds['filename'],
                hash=ds['hash'],
                size=ds['size'],
                model=ds_data_model,
                homepage_url=app.config['HomepageURL'],
                mcc_version=str(mcc_version)
            )
        elif info['response'] == 'pdf':
            print_styles_css_path = join('static', 'css', 'print-styles.css')

            html = render_template(
                'results_pdf.html',
                selected_checkers=selected_checkers,
                results=results,
                fn=ds['filename'],
                hash=ds['hash'],
                size=ds['size'],
                model=ds_data_model,
                mcc_version=str(mcc_version),
                homepage_url=app.config['HomepageURL'],
                print_styles_css_path=print_styles_css_path
            )

            options = {
                'page-size': 'Letter',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'enable-local-file-access': None,
                'quiet': ''
            }

            pdf = pdfkit.from_string(html, False, options=options)

            response = make_response(pdf)
            response.headers["Content-Disposition"] = f'attachment;filename={ds["filename"]}_metadata_compliance_report.pdf'
            response.mimetype = 'application/pdf'
        else:
            return abort(
                400, 'Invalid value for "response". Accepted response types are "html", "json", and "pdf".'
            )

    return response


@app.route('/about')
def about():
    """
    Returns the "About" page using the current MCC configuration.
    """
    return render_template(
        'about.html',
        checkers=[checker.ABOUT for checker in list(CHECKERS.values())],
        homepage_url=app.config['HomepageURL'],
        mcc_version=str(mcc_version)
    )


@app.route('/about_api')
def about_api():
    """
    Returns the "About API" page using the current MCC configuration.
    @return rendered version of the about_api.html template.
    """
    return render_template(
        'about_api.html',
        max_size=format_byte_size(app.config['MAX_CONTENT_LENGTH'],),
        homepage_url=app.config['HomepageURL']
    )


@app.route('/')
def index():
    """
    Main index for the MCC webpage.
    @return template with checker details and max file size (human-readable) provided
    """
    return render_template(
        'index.html',
        checkers=[checker.ABOUT for checker in list(CHECKERS.values())],
        max_file_size=format_byte_size(app.config['MAX_CONTENT_LENGTH']),
        max_file_size_bytes=app.config['MAX_CONTENT_LENGTH'],
        mcc_version=str(mcc_version),
        venue=(app.config['Venue'])
    )
