"""
=============
file_utils.py
=============

Utility functions for the web interface to use when dealing with files.
"""

import gzip
import logging
import os.path
import tempfile
from gzip import BadGzipFile
from hashlib import md5
from os.path import getsize

import bz2file as bz2
from flask import abort, current_app
from netCDF4 import Dataset

app = current_app

logger = logging.getLogger(__name__)


def hash_file(infile, hasher=None, blocksize=8388608):  # 8MB buffer (8 * 1024 * 1024)
    """
    Incrementally generate file hashes (suitable for very large files).
    Uses a large buffer size (8MB) for better performance with multi-GB files.

    @param infile a python file-like object
    @param hasher a hasher function from hashlib library (e.g. md5, sha256, ...)
    @param blocksize an integer of bytes to read into the hash at a time (default: 8MB)
    @return a hexdigest of the hash based on the hasher
    """
    if hasher is None:
        hasher = md5()

    # Save current file position
    current_pos = infile.tell()
    
    # Go to beginning of file
    infile.seek(0)
    
    # Read and hash in chunks
    buf = infile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = infile.read(blocksize)

    # Reset file buffer back to original position
    infile.seek(current_pos)

    return hasher.hexdigest()


def format_byte_size(n_bytes):
    """
    Gets a human-readable representation of a file size.

    @param n_bytes size of a file in bytes as a number
    @return a string representation of that size with the largest correct units
    """
    for unit in ('bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'):
        if n_bytes < 1000.0:
            return f'{n_bytes:3.2f} {unit}'

        n_bytes /= 1000.0

    # If we exit the loop, then n_bytes is larger than 1024 yottabytes.
    return 'pretty big'


def decompress_file(infile, upload_filename):
    """
    Opens gzip and bz2 files and returns the uncompressed data.
    Optimized for handling large files (4GB+) efficiently.
    Uncompresses in pieces and cuts off when limit is reached to avoid 'zip bombs'.

    @param infile file object containing the data to decompress
    @param upload_filename name of the file to decompress
    @return a temporary file object containing the decompressed data
    """
    app.logger.info("Decompressing file %s", upload_filename)

    # Use the configured temporary directory for large file processing
    temp_dir = app.config.get('TEMP_FILE_DIR', tempfile.gettempdir())
    decompressed_file = tempfile.NamedTemporaryFile(dir=temp_dir)
    extension = os.path.splitext(upload_filename)[-1].lower()

    # Determine the correct open function based on the type of decompression
    if extension == ".gz":
        open_fn = gzip.open
    elif extension == ".bz2":
        open_fn = bz2.open
    else:
        raise ValueError(f"Unknown file extension ({extension}) for decompression")

    # Use a larger buffer size for better performance with large files
    buffer_size = 8 * 1024 * 1024  # 8MB buffer

    try:
        data_length = 0
        reader = open_fn(infile)

        # Stream decompression with a larger buffer
        while data_length < app.config['MAX_CONTENT_LENGTH']:
            buf = reader.read(buffer_size)

            if len(buf) == 0:
                break

            data_length += len(buf)
            decompressed_file.write(buf)
        else:
            # If we exit the loop without breaking, the file is too large
            decompressed_file.close()
            return abort(
                400, f"The decompressed file size is too large. "
                     f"Max decompressed file size is: {format_byte_size(app.config['MAX_CONTENT_LENGTH'])}. "
                     f"Filename: {upload_filename}"
            )
            
        # Close the reader to free resources
        reader.close()
        
    except (BadGzipFile, OSError, ValueError, TypeError, IOError, EOFError) as err:
        decompressed_file.close()
        raise ValueError(
            f'Failed to decompress {extension} file {upload_filename}, reason: {str(err)}.'
        )
    except MemoryError:
        # Handle memory errors from bzip bombs
        decompressed_file.close()
        return abort(
            400, f"The decompressed file size is too large or caused a memory error. "
                 f"Max decompressed file size is: {format_byte_size(app.config['MAX_CONTENT_LENGTH'])}. "
                 f"Filename: {upload_filename}"
        )

    # Roll file pointer back to beginning of buffer now that decompression is complete
    decompressed_file.seek(0)
    app.logger.info(f"Successfully decompressed {upload_filename} to size {format_byte_size(data_length)}")

    return decompressed_file


def get_dataset_from_file(uploaded_file):
    """
    Derives a netcdf4.Dataset object from the provided file upload dictionary.
    Optimized for handling large files (4GB+) efficiently.

    @param uploaded_file open file handle or path to the data to convert.
    """
    app.logger.info("Attempting to get dataset from uploaded file %s", uploaded_file)
    
    # Handle both file paths and file objects
    if isinstance(uploaded_file, str):
        # It's a file path
        datafile_name = os.path.basename(uploaded_file)
        is_path = True
    else:
        # It's a file object
        datafile_name = uploaded_file.filename
        is_path = False
    
    check_valid_filename(datafile_name)
    
    # For large files, we want to avoid loading the entire file into memory
    # Instead, we'll use a temporary file and stream the data in chunks
    
    # Use the configured temporary directory for large file processing
    temp_dir = app.config.get('TEMP_FILE_DIR', tempfile.gettempdir())
    
    # Create a named temporary file in the specified directory
    datafile = tempfile.NamedTemporaryFile(dir=temp_dir, suffix=f"_{datafile_name}")
    
    # Stream the file in chunks to avoid memory issues
    if is_path:
        # If it's a path, open the file and copy it
        with open(uploaded_file, 'rb') as src_file:
            # Use a larger buffer size (8MB) for faster copying of large files
            buffer_size = 8 * 1024 * 1024  # 8MB buffer
            while True:
                buffer = src_file.read(buffer_size)
                if not buffer:
                    break
                datafile.write(buffer)
    else:
        # If it's a file object, stream from it
        # Use a larger buffer size (8MB) for faster copying of large files
        buffer_size = 8 * 1024 * 1024  # 8MB buffer
        while True:
            buffer = uploaded_file.read(buffer_size)
            if not buffer:
                break
            datafile.write(buffer)
    
    # Reset file pointer to beginning
    datafile.seek(0)

    # Calculate hash and file size now, prior to any potential file decompression
    file_hash = hash_file(datafile)
    file_size = format_byte_size(getsize(datafile.name))

    # Send compressed files to decompressor
    if datafile_name.lower().endswith(('.gz', '.bz2')):
        try:
            decompressed_file = decompress_file(datafile, datafile_name)
        except ValueError as err:
            return abort(
                500, f'Failed to decompress file {datafile_name}, reason: {str(err)}.'
            )
        finally:
            # Should no longer need the compressed version of file
            datafile.close()

        datafile = decompressed_file

    try:
        return {
            'dataset': Dataset(datafile.name, 'r'),
            'hash': file_hash,
            'size': file_size,
            'filename': datafile_name
        }
    except Exception as err:
        return abort(
            500, f"Error processing file {datafile_name}, reason: {str(err)}. "
                 f"Please make sure it's a valid NetCDF file."
        )
    finally:
        datafile.close()


def check_valid_filename(filename):
    """
    Checks if the provided file name conforms to one of the expected input types.

    @param filename Name of the file to check
    """
    if not filename.lower().endswith(('.gz', '.bz2', '.nc', '.hdf', '.h5', '.nc4')):
        return abort(
            500, f'File {filename} is not in an accepted data format. '
                 f'Must be one of .gz, .bz2, .nc, .h5, .nc4 or .hdf.'
        )
