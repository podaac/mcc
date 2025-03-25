# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Added client-side upload file size check that disables upload submission when a user selects a file that exceeds the limit set by server
### Changed
- **PODAAC-5873**
  - Made several updates to file utility functions to ensure temporary files are always deleted after use
  - Updated /check endpoint to ensure NetCDF4 object is always closed when we are finished with it
  - Added unit test to ensure no temporary files remain after processing an input file attachment 
- **PODAAC-5694**
  - Updated Build/Deploy Jenkinsfiles to support deployments to NGAP instead of on-prem
### Deprecated
### Removed
- **PODAAC-6763**
  - Reworked patching of the CF compliance checker suite in cf_shim.py such that the version copied from pythonlibs/suite.py
    is no longer required when building the container for MCC.
  - Various files have been sanitized to remove references to PO.DAAC resources such as server names or URLs
### Fixed
  - Fixed issue where venue name was hardcoded to "SIT" within the index.html template
- **PODAAC-6722**
  - Fixed issue where results page/tab did not have an associated URL to allow users to refresh without losing contents
- **PODAAC-6686**
  - Fixed issue where human-readable file sizes in webapp did not match what the OS could report
### Security
- **PODAAC-5680**
  - Updated Terraform scripts to include the ngap-dit-proxy container within the Fargate deployment

## [v1.5.0]
### Added
### Changed
### Deprecated
### Removed
### Fixed
- **PODAAC-6081**
  - Fixed margin usage for PDF reports so text is not cut off between pages
  - Overhauled progress bar to track upload progress from client side
- **PODAAC-6582**
  - MCC codebase has been tidied up to remove unused files, cleanup documentation and fix bugs
  - The CF checker shim now patches the "check_calendar" test to remove an unhelpful daterange check that caused a performance bottleneck
### Security

## [v1.4.2]
### Added
- **Podaac-5695**
  - Added POST method for MCC / Check test API
  - Created test cases and related steps
- **PODAAC-6034**
  - Added warning when uploading large file
  - Added upload status bar in UI
- **Podaac-5754**
  - Added TestRail API Interface
  - Added dependencies list
  - Created dummy API test case
  - Created config files and input customization structure
  - Added environment file
  - Added File handling
  - Added Selenium basic interface
  - Added Cleanup
  - Defined before/after hooks
  - Added behave local execution script
  - Extended gitignore
- **Podaac-5755**
  - Added script for docker execution
  - Added CreateFile method to FileHandler
  - Added updateComponentVersion script
- **PODAAC-5679**
  - Added Terraform for ECS, deployed MCC in Fargate application
- **PODAAC-5755**
  - Added Terraform for AWS Load Balancer
- **Podaac-5756**
  - Updated env.sample
  - Added Brwoser information to UI Testrail report
  - Added UI E2E tests
  - Added MCC main and report page steps
  - Added MCC main and report page handling
  - Added Selenium handling for dropdowns
- **PODAAC-5701**
  - Added Snyk Security Scan and test to Jenkins pipeline
- **PODAAC-5875**
  - Add MCC version to UI and html/pdf Reports
- **PODAAC-5984**
  - Add ACDD, CF, GDS2 Checker versions to report and API response
- **PODAAC-6097**
  - Update Load Balancer listener protocol and port to HTTPS 443. Use ACM issued certificate via NGAP instructions.
- **PODAAC-6224**
  - Added file close even on exception
  - Added test files
  - Added File Size Verification
  - Added file PID blocking handling
  - Added new API file format tests
  - Extended non 200 API tests with error message check
  - Created error page for MCC UI test
  - Added oversized file tests for UI
  - Added reading MCC limit info from website instead of file
  - Updated pdf report verification
- **API request/response fix** 
  - API call fix. As a prereq for automation test - PODAAC-6106
- **PODAAC-6173**
  - Add Google Analytics Tagging. Disable tags in SIT/UAT. Enable in OPS.
  - Security fix for CWE-548 directory exposure 
- **PODAAC-6289**
  - Added new test for empty file check
  - Added large file warning to the oversized UI test
  - Changed large file size for API test
  - Added timout exception handling for click selenium element
  - Added wait time modifications to selenium findelements
  - Added bool return to waitForPage instead of exception
### Changed
- **PODAAC-5670**
  - Set versions for Python packages
  - Upgrade MCC Docker Image to Python3.8
- **PODAAC-5743**: Disable importing remote netCDF file via OPeNDAP
- **PODAAC-5723**: Updated Webpage PODAAC header and footer, removed levels of service and outdated menu bar
- **PODAAC-5688**: Manual Snyk pip test in MCC Docker Container. Fixed vulnerabilities.
- **PODAAC-6077**
  - Clean up OPeNDAP references in error message for missing file attachment
- **PODAAC-5728**: Updated GHRSST GDS 2.1 Revision 0 Data Specification link
- **PODAAC-6106**
  - Added checker version verifiation to API and UI tests
  - Updated API test s behavior to reflect current one
  - Added selenium version verification
  - Added OS version verification
  - Added default temp and download dir
  - Added comments for seleium setup to show settings in log
  - Some formating for string to use ' instead of "
  - Created Test Case ignore mechanism
### Deprecated
### Removed
### Fixed
### Security

## [v1.4.0] - 2021-07-26
### Added
- **PODAAC-2934**
  - Docker-compose file added for local machine deployment of MCC
  - Added CF Checker version 1.7 to MCC, with dropdown toggle for (1.6, 1.7)
- PODAAC-3129: MCC updated form Python 2.7 --> Python 3.6. With centOS7 Build.
### Changed
- PODAAC-2934: CF Convention Standard Names Table updated to version 77 and updated MCC python dependencies with maintained library versions
### Deprecated
### Removed
- PODAAC-3329: Removed CF 9.1 variable-level featureType check from compliance report
### Fixed
- PODAAC-3444: Reset ENTRYPOINT on Dockerfile for testbed deployment fix, and resolved ACDD checker file upload error for file 265669_NSIDC-0738-EASE2_N25km-SMAP_LRM-2017001-1.4H-M-GRD-JPL-v2.0.nc

- fix/UAT_Tests: MCC failing checker results for 4/10 UAT test cases. Errors include: "Unable to read file" and "Gateway Timeout"
  - Fixed: 10/10 UAT Test Cases pass
  - Fixed: Compressed NC file upload works. Both .gz and .bz2
  - Not Fixed: HDF file uploads fail. netCDF Dataset reader not recognizing file format
### Security
