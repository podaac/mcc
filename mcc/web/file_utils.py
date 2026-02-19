"""
=============
file_utils.py
=============

Utility functions for the web interface to use when dealing with files.
Optimized for high-performance handling of 1GB+ NetCDF files.
"""

import gzip
import logging
import os.path
import tempfile
import shutil
from gzip import BadGzipFile
from hashlib import md5
from os.path import getsize

import bz2file as bz2
from flask import abort, current_app
from netCDF4 import Dataset

app = current_app
logger = logging.getLogger(__name__)

# Increase chunk size to 64KB for faster I/O on large files
CHUNK_SIZE = 65536


def hash_file(infile, hasher=None, blocksize=CHUNK_SIZE):
    """
    Memory-efficient file hashing using chunks.
    """
    if hasher is None:
        hasher = md5()

    infile.seek(0)
    while True:
        buf = infile.read(blocksize)
        if not buf:
            break
        hasher.update(buf)
    
    # Reset file buffer back to starting position
    infile.seek(0)
    return hasher.hexdigest()


def format_byte_size(n_bytes):
    """
    Gets a human-readable representation of a file size.
    """
    for unit in ('bytes', 'KB', 'MB', 'GB', 'TB'):
        if n_bytes < 1000.0:
            return f'{n_bytes:3.2f} {unit}'
        n_bytes /= 1000.0
    return 'pretty big'


def decompress_file(infile, upload_filename):
    """
    Opens gzip and bz2 files and returns a temporary file object.
    Uses streaming to avoid memory spikes and protects against zip bombs.
    """
    app.logger.info("Decompressing file %s", upload_filename)

    # delete=False allows the file to persist so netCDF4 can open it by path
    decompressed_file = tempfile.NamedTemporaryFile(delete=False)
    extension = os.path.splitext(upload_filename)[-1]

    if extension == ".gz":
        open_fn = gzip.open
    elif extension == ".bz2":
        open_fn = bz2.open
    else:
        raise ValueError(f"Unknown file extension ({extension}) for decompression")

    try:
        data_length = 0
        reader = open_fn(infile)

        while True:
            # Check against MAX_CONTENT_LENGTH before reading more
            if data_length > app.config.get('MAX_CONTENT_LENGTH', 2 * 1024**3):
                raise ValueError("Decompressed size exceeds limit.")

            buf = reader.read(CHUNK_SIZE)
            if not buf:
                break

            data_length += len(buf)
            decompressed_file.write(buf)

    except Exception as err:
        decompressed_file.close()
        if os.path.exists(decompressed_file.name):
            os.remove(decompressed_file.name)
        raise ValueError(f'Failed to decompress {upload_filename}: {str(err)}')

    decompressed_file.seek(0)
    return decompressed_file


def get_dataset_from_file(uploaded_file):
    """
    Derives a netcdf4.Dataset object from the provided file upload.
    Refactored to stream data to disk instead of loading 1.2GB into RAM.
    """
    app.logger.info("Attempting to get dataset from uploaded file %s", uploaded_file.filename)

    datafile_name = uploaded_file.filename
    check_valid_filename(datafile_name)

    # Create a named temporary file to store the upload on disk
    datafile = tempfile.NamedTemporaryFile(suffix=f"_{datafile_name}", delete=False)
    
    # STREAM the file from the request to the disk
    shutil.copyfileobj(uploaded_file, datafile)
    datafile.seek(0)

    # Calculate hash and size from the disk file
    file_hash = hash_file(datafile)
    file_size = format_byte_size(getsize(datafile.name))

    # Handle compression
    if datafile_name.lower().endswith(('.gz', '.bz2')):
        try:
            decompressed_result = decompress_file(datafile, datafile_name)
            # Close and remove the compressed version to free up disk space
            datafile.close()
            if os.path.exists(datafile.name):
                os.remove(datafile.name)
            datafile = decompressed_result
        except ValueError as err:
            return abort(500, f'Decompression error: {str(err)}')

    try:
        # Open by filename (allows netCDF4 to use memory-mapping)
        return {
            'dataset': Dataset(datafile.name, 'r'),
            'hash': file_hash,
            'size': file_size,
            'filename': datafile_name,
            'temp_path': datafile.name # Keep track for later cleanup
        }
    except Exception as err:
        datafile.close()
        if os.path.exists(datafile.name):
            os.remove(datafile.name)
        return abort(500, f"NetCDF Error: {str(err)}")


def check_valid_filename(filename):
    """
    Checks if the provided file name conforms to expected types.
    """
    valid_exts = ('.gz', '.bz2', '.nc', '.hdf', '.h5', '.nc4')
    if not filename.lower().endswith(valid_exts):
        return abort(400, f'Unsupported file format. Must be one of: {", ".join(valid_exts)}')
