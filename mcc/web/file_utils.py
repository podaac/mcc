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


def hash_file(infile, hasher=None, blocksize=65536):
    """
    Incrementally generate file hashes (suitable for large files).

    @param infile a python file-like object
    @param hasher a hasher function from hashlib library (e.g. md5, sha256, ...)
    @param blocksize an integer of bytes to read into the hash at a time
    @return a hexdigest of the hash based on the hasher
    """
    if hasher is None:
        hasher = md5()

    buf = infile.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)
        buf = infile.read(blocksize)

    # Reset file buffer back to starting position
    infile.seek(0)

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
    Uncompresses in pieces andand cuts off when limit is reached in order to
    avoid 'zip bombs'.

    Solution suggested by Mark Adler:
    http://stackoverflow.com/questions/13622706/how-to-protect-myself-from-a-gzip-or-bzip2-bomb

    The gist is that we decompress the file in chunks, counting the uncompressed
    size of each and adding it to the total. If the filesize is OK, then
    decompress the file and return data. This seems a little redundant, but
    uncompressing the actual file in chunks and storing the data creates
    crashing issues in the Docker container.

    TODO: Bz2 doesn't have the same ability as zlib to read in chunks, so a bomb is
          just going to cause a memory error. So, given the extra time it takes to
          decompress a bz2, I'm just assembling the chunks on the fly instead of
          unzipping a second time. Investigate a workaround for this at some point.

    @param infile file object containing the data to decompress
    @param upload_filename name of the file to decompress
    @return a temporary file object containing the decompressed data
    """
    app.logger.info("Decompressing file %s", upload_filename)

    decompressed_file = tempfile.NamedTemporaryFile()
    extension = os.path.splitext(upload_filename)[-1]

    # Determine the correct open function based on the type of decompression
    if extension == ".gz":
        open_fn = gzip.open
    elif extension == ".bz2":
        open_fn = bz2.open
    else:
        raise ValueError(f"Unknown file extension ({extension}) for decompression")

    try:
        data_length = 0
        reader = open_fn(infile)

        while data_length < app.config['MAX_CONTENT_LENGTH']:
            buf = reader.read(1024)

            if len(buf) == 0:
                break

            data_length += len(buf)
            decompressed_file.write(buf)
        else:
            decompressed_file.close()
            return abort(
                400, f"The decompressed file size is too large. "
                     f"Max decompressed file size is: {format_byte_size(app.config['MAX_CONTENT_LENGTH'])}. "
                     f"Filename: {upload_filename}"
            )
    except (BadGzipFile, OSError, ValueError, TypeError, IOError, EOFError) as err:
        decompressed_file.close()
        raise ValueError(
            f'Failed to decompress {extension} file {upload_filename}, reason: {str(err)}.'
        )
    except MemoryError:
        # Noticed that some bzip bombs cause memory errors. There doesn't
        # seem to be a ton of great ways around this.
        decompressed_file.close()
        return abort(
            400, f"The decompressed file size is too large. "
                 f"Max decompressed file size is: {format_byte_size(app.config['MAX_CONTENT_LENGTH'])}. "
                 f"Filename: {upload_filename}"
        )

    # Roll file pointer back to beginning of buffer now that decompression is complete
    decompressed_file.seek(0)

    return decompressed_file


def get_dataset_from_file(uploaded_file):
    """
    Derives a netcdf4.Dataset object from the provided file upload dictionary.

    @param uploaded_file open file handle to the data to convert.
    """
    app.logger.info("Attempting to get dataset from uploaded file %s", uploaded_file)

    datafile_name = uploaded_file.filename
    check_valid_filename(datafile_name)

    # uploaded_file is an instance of werkzeug.FileStorage, which only allows us
    # to read the file contents but not reference a location on disk.
    # Copy the uploaded file to a named temporary file, so we can provide a disk
    # location when initializing the netCDF.Dataset object below.
    datafile = tempfile.NamedTemporaryFile()
    datafile.write(uploaded_file.read())
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
