"""
=========
server.py
=========

Flask server front end for the MCC service.
Optimized for handling large NetCDF files (1GB+) with memory-efficient streaming.

This implementation includes:
- Direct file streaming to disk to avoid memory issues
- Asynchronous processing for large files using Celery
- Synchronous processing for smaller files
- Proper resource cleanup to avoid disk space issues
"""

# Standard library imports for file handling and system operations
import time
import os
import uuid  # For generating unique IDs for temporary files
import shutil  # For efficient file copying operations
from os import environ
from os.path import join

# Third-party imports
import pdfkit  # For PDF generation
from flask import Flask, render_template, request, abort, jsonify, make_response, url_for
from celery.result import AsyncResult  # For checking async task status

# Local application imports
from checker.acdd import ACDD  # ACDD compliance checker
from checker.cf_shim import CF  # CF compliance checker
from checker.gds2 import GDS2  # GDS2 compliance checker
from .file_utils import format_byte_size, get_dataset_from_file  # Optimized file handling utilities
from .form_utils import parse_post_arguments  # Form parsing utilities
from .json_utils import CustomJSONEncoder  # JSON serialization utilities
from .tasks import process_large_file  # Asynchronous processing task

# Initialize Flask application
app = Flask(__name__)

# Style options for whitespace in templated HTML code
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# The JSON encoder in use when we call flask.jsonify()
app.json_encoder = CustomJSONEncoder

# Maximum allowed file size when submitting directly to service via API
app.config['MAX_CONTENT_LENGTH'] = int(environ.get('ApiMaxFileSize', 10 * 1024**3))

# Maximum allowed file size when submitting via the Web frontend
app.config['UiMaxFileSize'] = int(environ.get('UiMaxFileSize', 10 * 1024**3))

# URL to use for MCC homepage
app.config['HomepageURL'] = environ.get('HomepageURL', '#')

# Venue that MCC is deployed to (SIT, UAT, or OPS)
app.config['Venue'] = str(environ.get('Venue', 'SIT'))

# Threshold for large file processing (in bytes)
app.config['LARGE_FILE_THRESHOLD'] = int(environ.get('LARGE_FILE_THRESHOLD', 1073741824))

# Directory for storing large files during processing
app.config['TEMP_FILE_DIR'] = environ.get('TEMP_FILE_DIR', '/tmp/mcc_large_files')

# Create temporary directory if it doesn't exist
os.makedirs(app.config['TEMP_FILE_DIR'], exist_ok=True)

# Register available compliance checkers
# Maps short names to checker classes for dynamic selection based on user input
CHECKERS = {
    ACDD.ABOUT['short_name']: ACDD,  # Attribute Convention for Dataset Discovery
    CF.ABOUT['short_name']: CF,      # Climate and Forecast Conventions
    GDS2.ABOUT['short_name']: GDS2,  # GHRSST Data Specification
}

# Get MCC version from VERSION file or use default if file not found
try:
    with open('/var/www/html/mcc/web/VERSION', 'r') as f:
        mcc_version = f.read().rstrip()
except:
    mcc_version = "1.0.0"  # Default version if VERSION file not found

def stream_save_upload(uploaded_file, destination):
    # Streams file uploads directly to disk without loading into memory
    # Critical for handling multi-GB files efficiently
    # Uses shutil.copyfileobj to stream in chunks instead of loading entire file
    with open(destination, 'wb') as f:
        shutil.copyfileobj(uploaded_file.stream, f)


# Error handlers for HTTP response codes
@app.errorhandler(413)
def req_entity_too_large(err):
    # Handle 413 Request Entity Too Large errors
    # This occurs when the uploaded file exceeds MAX_CONTENT_LENGTH
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
    # Main endpoint for file validation and compliance checking
    # Handles both synchronous (small files) and asynchronous (large files) processing
    # Large files are processed in the background using Celery
    request_dict = request.form
    resp_type = request_dict.get('response')

    if not resp_type:
        return abort(400, 'Missing "response" parameter (json, html, or pdf).')

    # Extract file without loading into RAM
    uploaded_file = request.files.get('file-upload')
    if not uploaded_file:
        return abort(400, 'No file uploaded.')

    filename = uploaded_file.filename
    
    # Calculate size using stream pointer without reading content
    # This is more memory efficient than loading the file to check its size
    uploaded_file.seek(0, os.SEEK_END)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)  # Reset pointer to beginning of file

    # Determine which checkers to run based on form input
    selected_checkers = {}
    if request_dict.get('ACDD') == 'on':
        selected_checkers['ACDD-version'] = request_dict.get('ACDD-version') or ACDD.DEFAULT_VERSION
    if request_dict.get('CF') == 'on':
        selected_checkers['CF-version'] = request_dict.get('CF-version') or CF.DEFAULT_VERSION
    if request_dict.get('GDS2') == 'on':
        selected_checkers['GDS2-parameter'] = request_dict.get('GDS2-parameter') or GDS2.DEFAULT_VERSION

    # ASYNC PATH: For files larger than the threshold (default: 1GB)
    if file_size > app.config['LARGE_FILE_THRESHOLD']:
        # Generate unique ID for this job
        job_id = str(uuid.uuid4())
        temp_path = os.path.join(app.config['TEMP_FILE_DIR'], f"{job_id}_{filename}")
        
        # Stream file directly to disk without loading into memory
        stream_save_upload(uploaded_file, temp_path)
        
        # Start asynchronous processing task
        task = process_large_file.delay(temp_path, filename, selected_checkers)
        
        # Return appropriate response based on requested format
        if resp_type == 'json':
            return jsonify({
                'status': 'processing',
                'task_id': task.id,
                'check_status_url': url_for('check_status', task_id=task.id, _external=True)
            })
        # For HTML/PDF responses, show processing page with status updates
        return render_template('processing.html', task_id=task.id, filename=filename)

    # SYNC PATH: For smaller files that can be processed immediately
    info = parse_post_arguments(request.form, request.files, CHECKERS)
    ds_container = get_dataset_from_file(info['file'])  # Memory-efficient dataset loading
    
    # Run selected checkers against the dataset
    results = []
    for checker in info['checkers']:
        results.append(checker.run(ds_container['dataset']))
    
    # Get data model and close dataset to free resources
    ds_data_model = ds_container['dataset'].data_model
    ds_container['dataset'].close()

    # Return JSON response if requested
    if resp_type == 'json':
        return jsonify({'results': results, 'size': ds_container['size']})
    
    # Clean up temporary files to avoid disk space issues
    if 'temp_path' in ds_container and os.path.exists(ds_container['temp_path']):
        try:
            os.remove(ds_container['temp_path'])
        except OSError:
            app.logger.error(f"Failed to remove temp file: {ds_container['temp_path']}")
        
    # Return HTML results page
    return render_template('results.html', results=results, fn=filename)


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
        checkers={checker.ABOUT['short_name']: checker.ABOUT for checker in list(CHECKERS.values())},
        max_size=format_byte_size(app.config['MAX_CONTENT_LENGTH'],),
        homepage_url=app.config['HomepageURL']
    )


@app.route('/check_status/<task_id>')
def check_status(task_id):
    # Check the status of an asynchronous processing task
    # Allows clients to poll for the status of a large file processing task
    # Returns the current state and any available progress information
    task_result = AsyncResult(task_id)  # Get task result from Celery
    response = {'status': task_result.state, 'info': task_result.info}
    return jsonify(response)

@app.route('/results/<task_id>')
def get_results(task_id):
    # Retrieve results of a completed asynchronous processing task
    # Returns results in the requested format (JSON or HTML)
    # Returns 404 error if the task is not yet complete
    task_result = AsyncResult(task_id)
    
    # Check if task is complete
    if task_result.state != 'SUCCESS':
        return abort(404, "Task not ready.")
    
    # Get the actual result data
    result = task_result.get()
    
    # Determine response format (default: JSON)
    format_type = request.args.get('format', 'json')

    if format_type == 'json':
        return jsonify(result)
    
    # For HTML format, pass all result fields to the template
    return render_template('results.html', **result)


@app.route('/')
def index():
    # Main landing page for the MCC service
    # Renders the index template with configuration information
    return render_template('index.html', 
        checkers=[checker.ABOUT for checker in list(CHECKERS.values())],
        max_ui_file_size=format_byte_size(app.config['UiMaxFileSize']),
        homepage_url=app.config['HomepageURL'],
        mcc_version=mcc_version
    )

@app.errorhandler(413)
def req_too_large(err):
    # Handle 413 Request Entity Too Large errors
    # Occurs when the uploaded file exceeds MAX_CONTENT_LENGTH
    return jsonify({'error': 'File too large'}), 413
