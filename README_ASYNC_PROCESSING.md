# MCC Asynchronous Processing for Large Files

This document describes the asynchronous processing feature for handling large file uploads in the Model Coupling Checker (MCC) system.

## Overview

The MCC system now supports asynchronous processing for large file uploads (over 1GB by default). This feature helps prevent timeouts when uploading and processing large NetCDF files.

## How It Works

1. When a file larger than the configured threshold is uploaded, it is saved to a temporary location
2. A background task is started to process the file
3. The user receives a task ID that can be used to check the status of the processing
4. Once processing is complete, the results can be retrieved in the requested format (JSON, HTML, or PDF)

## Configuration

The following environment variables can be configured:

- `LARGE_FILE_THRESHOLD`: Size threshold in bytes for asynchronous processing (default: 1GB)
- `TEMP_FILE_DIR`: Directory for storing temporary files during processing (default: `/tmp/mcc_large_files`)
- `CELERY_BROKER_URL`: URL for the Celery broker (default: `redis://localhost:6379/0`)
- `CELERY_RESULT_BACKEND`: URL for the Celery result backend (default: `redis://localhost:6379/0`)

## Timeout Settings

The following timeout settings have been updated to better handle large file uploads:

1. **Apache Timeout**: Increased to 3600 seconds (1 hour)
2. **WSGI Inactivity Timeout**: Increased to 3600 seconds (1 hour)
3. **Request Read Timeout**: Set to 3600 seconds (1 hour) for the request body

## API Usage

### Uploading Large Files

Upload files as usual to the `/check` endpoint. If the file is larger than the threshold, you'll receive a response with:

```json
{
  "status": "processing",
  "job_id": "unique-job-id",
  "task_id": "celery-task-id",
  "filename": "your-file.nc",
  "file_size": "1.2 GB",
  "check_status_url": "https://mcc.podaac.earthdatacloud.nasa.gov/check_status/celery-task-id"
}
```

### Checking Status

Check the status of a task by sending a GET request to:

```
GET /check_status/{task_id}
```

Response:

```json
{
  "status": "PENDING|PROCESSING|SUCCESS|FAILURE",
  "info": "Additional information"
}
```

### Retrieving Results

Once processing is complete, retrieve the results by sending a GET request to:

```
GET /results/{task_id}?format=json|html|pdf
```

## Command Line Usage

For uploading large files via curl, use extended timeout parameters:

```bash
curl -v -L --connect-timeout 300 --max-time 3600 --keepalive-time 3600 \
  -F ACDD=on -F ACDD-version=1.3 -F CF=on -F CF-version=1.9 \
  -F file-upload=@/path/to/large/file.nc -F response=json \
  https://mcc.podaac.earthdatacloud.nasa.gov/check
```

## Deployment Requirements

To use this feature, the following components must be deployed:

1. Redis server for Celery task queue
2. Celery workers configured to process tasks
3. Updated Apache configuration with the new timeout settings

## Cleanup

Temporary files are not automatically deleted. A cron job should be set up to clean old files from the temporary directory:

```bash
# Example cron job to clean files older than 7 days
0 0 * * * find /tmp/mcc_large_files -type f -mtime +7 -delete
```
