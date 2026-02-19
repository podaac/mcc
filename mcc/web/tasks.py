"""
=======
tasks.py
=======

Celery tasks for asynchronous processing of large files.
Optimized for memory efficiency (streaming) for files > 1GB.
"""

import time
import os
import shutil
import tempfile
from hashlib import md5
from os.path import getsize

from netCDF4 import Dataset
from flask import current_app

from .celery_app import celery_app
from .file_utils import format_byte_size, decompress_file

@celery_app.task(bind=True)
def process_large_file(self, file_path, filename, selected_checkers):
    """
    Process a large file asynchronously with memory-safe streaming.
    """
    app = current_app._get_current_object()
    temp_file_path = None
    
    try:
        # 1. Update State: Hashing
        self.update_state(state='PROGRESS', meta={'status': 'Calculating file hash...'})
        
        file_size_raw = getsize(file_path)
        file_size_pretty = format_byte_size(file_size_raw)
        
        with open(file_path, 'rb') as f:
            file_hash = hash_file(f)

        # 2. Decompression Logic (Streaming)
        # If it's a netCDF/HDF5 file already, we use the existing path to save IO
        current_working_path = file_path
        
        if filename.lower().endswith(('.gz', '.bz2')):
            self.update_state(state='PROGRESS', meta={'status': 'Decompressing file...'})
            with open(file_path, 'rb') as compressed_f:
                # Assuming decompress_file returns a file-like object or path
                decompressed_obj = decompress_file(compressed_f, filename)
                
                # Stream decompression to a temporary disk location to save RAM
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as tmp:
                    shutil.copyfileobj(decompressed_obj, tmp)
                    temp_file_path = tmp.name
                    current_working_path = temp_file_path
                decompressed_obj.close()

        # 3. Load Dataset
        self.update_state(state='PROGRESS', meta={'status': 'Opening NetCDF dataset...'})
        
        # Import checkers inside task to avoid circular dependencies
        from checker.acdd import ACDD
        from checker.cf_shim import CF
        from checker.gds2 import GDS2
        
        checkers = []
        if 'ACDD-version' in selected_checkers:
            checkers.append(ACDD(selected_checkers['ACDD-version']))
        if 'CF-version' in selected_checkers:
            checkers.append(CF(selected_checkers['CF-version']))
        if 'GDS2-parameter' in selected_checkers:
            checkers.append(GDS2(selected_checkers['GDS2-parameter']))

        try:
            # We open the file path directly (Dataset handles large files via disk-mapping)
            ds = Dataset(current_working_path, 'r')
            ds_data_model = ds.data_model
            
            results = []
            for checker in checkers:
                status_msg = f"Running {checker.name} ({checker.version})..."
                self.update_state(state='PROGRESS', meta={'status': status_msg})
                app.logger.info(status_msg)
                
                start = time.time()
                results.append(checker.run(ds))
                end = time.time()
                
                app.logger.info(
                    "Checker %s completed in %.3f seconds", checker.name, end - start
                )
            
            ds.close()
            
            return {
                'status': 'completed',
                'selected_checkers': selected_checkers,
                'fn': filename,
                'md5': file_hash,
                'size': file_size_pretty,
                'model': ds_data_model,
                'results': results
            }
            
        except Exception as err:
            app.logger.exception("NetCDF Processing Error")
            return {
                'error': 'Error processing file',
                'description': f"Error processing {filename}: {str(err)}. Ensure it is a valid NetCDF file."
            }
            
    except Exception as e:
        app.logger.exception("Unexpected Task Failure")
        return {
            'error': 'Unexpected error',
            'description': f"An unexpected error occurred: {str(e)}"
        }
    finally:
        # Cleanup: Remove the temporary decompressed file if one was created
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                app.logger.error("Failed to clean up temp file: %s", temp_file_path)

def hash_file(infile, hasher=None, blocksize=65536):
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
    
    infile.seek(0)
    return hasher.hexdigest()
