# Metadata Compliance Checker (MCC)
### Automated Metadata Validation for NetCDF Files

## Overview
MCC is a web-based tool that validates metadata from NetCDF files against various conventions. Users can either upload the file to be checked via a web form or submit a file via REST API. MCC then produces a report on the ways in which the file does or does not comply with the chosen conventions.

## Running MCC with Docker
-------
MCC is most easily run in a Docker "container" -- a single process similar to a VM that contains the necessary environment. You can share directories from the host computer inside the Docker container, and also map ports inside the Docker container to ones on the host machine.

#### A Note About Ports
Docker containers must each be bound to a specific port on the host machine, which is then forwarded to another port within the Docker container (usually 80 for HTTP and 443 for HTTPS). This port can then only be used with that specific container. So if you bind port 80 on the host machine to the MCC Docker container (with the `-p 80:80` option), the only application that can then use that port is MCC.

To run multiple Docker containers on the same machine, you'll want to run each container on a non-privileged port and use a proxy that can map paths to ports.

#### Build Docker Image
First you will need to build the Docker image. This sets up the MCC environment with the appropriate OS and packages. From the base of this repo, run:

`sudo docker build -t mcc .`

The build process may take a while, and Docker will need internet access at this time.

Note that, by default, the Docker image is built using the "ops" venue configuration, which defines a specific homepage URL, upload file size limit and temp file locations to be used by the MCC service when deploying to the OPS venue.
To build using the configuration for a different venue (such as UAT or SIT), specify a value for the `VENUE` build variable within the `docker build` command:

`sudo docker build --build-arg VENUE=[ops|uat|sit] -t mcc .`

#### Start MCC Docker Container
To start running a Docker container, use the following command:

`sudo docker run --name mcc -d -p <desired_external_port>:80 -v <tempfile_holding_area>:/tmp/mcc -v <location_of_logfiles>:/var/log/httpd -v <location_of_defines_conf>:/home/mcc/env  mcc:latest`

MCC requires you to share a few directories on the host computer with the Docker container. They are as follows:

**Temporary Files** - `<tempfile_holding_area>:/tmp/mcc` -- This location stores any uploads that are too large to fit in memory. Python deletes these files when it has finished processing them. This location should have more space than the maximum file size limit. Note that this location should have  read/write access for all users.

**Apache Log Files (Optional)** - `<location_of_logfiles>:/var/log/httpd` -- This specifies an external location where PODAAC.Drive's Apache log files will be stored.

**Environment Variables** - `<location_of_defines_conf>:/home/mcc` -- This points MCC to a file containing the necessary configuration options for your installation environment. Please view the comments in `defines.conf` and `logrotate.conf` for more details.

#### Stop MCC Docker Container
To stop a running MCC Docker container, use the following command:

`sudo docker stop mcc`

#### See MCC Docker Container Status
Use the `sudo docker ps` command to see all running containers on the machine. If MCC is running, you'll see a line with its status information. If you don't see the MCC container, it's either stopped or has been deleted. Use `sudo docker ps -a` to see all current containers that exist on the machine.

#### Resume MCC Docker Container
To resume a previously stopped MCC Docker container, use:

 `sudo docker start mcc`

**Note that the container will retain the original parameters for ports and shared directories that you specified in the initial `docker run` command. To change these options, remove the existing `mcc` container and enter a new `docker run` command.**

#### Delete MCC Docker Container
If you have a container you no longer want to run, or want to replace it with a new container that has different `docker run` parameters, use this command:

`sudo docker rm mcc`

Note that you'll need to run `docker stop` on the container first if it is already running.

#### Delete MCC Docker Image
If you want to delete MCC entirely from the machine, or you want to rebuild the image with the `docker build` command, use the `docker rmi` command as follows:

`sudo docker rmi mcc`

Note that all containers on the system that use the mcc image will need to be stopped and removed before the base image can be deleted.

---

### Apache Logfile Rotation
MCC is configured by default to rotate all the Apache log files on a monthly basis. The rotation options can be customized by editing the `logfile.conf` file, which is contained in the environment variables directory (a sample configuration file is provided in `env/sample_defines/logfile.conf`). 

For more information on how to customize the log file rotation, check out the comments in `logfile.conf` or run `man logrotate`. Restarting the Docker container is required for new changes to take place.


========

## Non-Docker Installation
------

### Dependencies:
* C libraries: HDF5, netCDF4, lxml libraries, swig, udunits2, apache, and numpy linalg (e.g. BLAS)
* Python 2.7
* Python packages: numpy and everything else in requirements.txt
* wkhtmltopdf
* mod_wsgi (if running in daemon mode)

Install all Python dependencies with `sudo pip install -r requirements.txt`

*Note: MCC dependency mod_wsgi currently does not work with Anaconda. Please use base Python 2.7*

### Configuration - Daemon Mode
In this mode, MCC runs within the system Apache instead of on its own. This allows MCC to use port 80 and share it with other pages on the same server.

Make sure that mod_wsgi is installed. Note that mod_wsgi must be compiled against the versions of Python and Apache that will be in use. It may be necessary to compile mod_wsgi instead of installing from an RPM.
 
The mod_wsgi module needs to be placed or linked into your Apache modules folder. 

mod_wsgi can be configured within the main httpd.conf file or in a separate file in the Apache conf.d directory. The file 'mcc_wsgi.conf' is included as a sample. In this file are notes for configuration.

#### The maximum file size for MCC is configured in the 'mcc_wsgi.conf' file. Please view that file for more information.

MCC error and access log entries will be contained in the main Apache logfiles.

After installing mod_wsgi into the Apache modules directory and configuring the wsgi.conf file, restart Apache.

Please refer to the [mod_wsgi documentation](https://code.google.com/p/modwsgi/wiki/InstallationIssues#Multiple_Python_Versions) for help with additional installation issues.

### Configuration - Standalone Mode (express)

### Startup
To start the MCC server, run this command from the root directory of the repo: 
`mod_wsgi-express start-server checker.wsgi --port 8080 --include-file ./checker.conf --server-root ./apache_server --log-level info`

**This command only needs to be run by `root` if the use of a privileged HTTP port (i.e. 80) is desired.**

#### The maximum file size for MCC is configured in the 'checker.conf' file. Please view that file for more information.

To use the checker, visit http://localhost:8080.

**The MCC server needs to be started manually. If you want it to start automatically when the machine boots, you'll need to add it to an init script.**

### Configuration
The following command-line options can be used to configure the server:
* `--port` specifies the HTTP port that the server will listen to. Use of privileged ports (i.e. 80) requires root privileges.
* `--server-root` specifies the location of the Apache config, log, and module files that will be generated. This can be anywhere, but it's important that the user running the server has full privileges for that directory.
* `--log-level` specifies the Apache log level. The error file (`error_log`) is located in the `--server-root` directory.

There's no need to modify the Apache config files in the `--server-root` directory. These are generated when you run the server startup command.

## Software Details
----
MCC is a Python application built in a [Flask](http://flask.pocoo.org/) web framework and served by the [mod_wsgi](https://github.com/GrahamDumpleton/mod_wsgi) Apache module.

### File Handling
MCC uses the Python [tempfile](https://docs.python.org/2/library/tempfile.html) library for handling of user-uploaded files. Uploaded files are placed in a temporary location and are protected from being excecutable.

File uploads are restriced to files with the extensions * .nc, * .hdf, * .h5, * .nc4, * .bz2, and * .gz. bzipped and gzipped archives are unpacked in 4kb chunks that concatenated together -- when the uncompressed data exceeds the maximum file upload size, the process is canceled and the data discarded.

MCC keeps no records of previously uploaded files and generated reports at this time. 

### mod_wsgi Server
[mod_wsgi](https://github.com/GrahamDumpleton/mod_wsgi)  is a commonly-used Apache module for serving Python web applications.

MCC utilizes a part of mod_wsgi called  **mod_wsgi-express**. Instead of requiring integration with the system-wide Apache configuration files, mod_wsgi-express uses the system's Apache libraries to run a customized instance on the user-selected port. The server uses the system version of Apache.

**mod_wsgi-express** creates its own configs -- it's not necessary to modify them or the system-wide Apache config. Nor is it necessary to install any modules aside from the mod_wsgi package that's available via `pip`.

### Caveats

-   checker.conf and web/server.py have a hard coded size limit that should be
    identical in both files

### Prior Art

* Dave Foster, Daniel Maher, and Luke Campbell's [compliance-checker](https://github.com/ioos/compliance-checker)
* Rosalyn Hatcher's [CF Compliance Checker](http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl)
* Ed Armstrong's [GDS2 Validator](ftp://podaac.jpl.nasa.gov/allData/ghrsst/sw/GDS2_validation/)
* THREDDS UDDC [ACDD Checker](http://thredds.jpl.nasa.gov/)
* The CF Conventions Group's Standard Names Table
