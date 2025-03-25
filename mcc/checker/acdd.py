
"""
=======
acdd.py
=======

CheckSuite definition for the Attribute Convention for Data Discovery (ACDD) standard.

TODO: parse geospatial_bounds using https://pypi.python.org/pypi/pygeoif
TODO: add 'did you mean...' type similarity checks for attributes (like currently exists for standard names)
TODO: check geospatial stuff based on data
TODO: check validity of time_coverage_duration as a delta
"""

from flask import abort

from .base import CheckSuite
from .checkers import (CheckExistence,
                       CheckCommaSeparated,
                       CheckStandardName,
                       CheckUDUnits,
                       CheckPossibleValues,
                       CheckISODatestuff,
                       CheckISODuration,
                       CheckDeprecated)


class ACDD(CheckSuite):
    ABOUT = {
        'name': 'Attribute Convention for Data Discovery',
        'short_name': 'ACDD',
        'url': 'http://wiki.esipfed.org/index.php/Attribute_Convention_for_Data_Discovery_1-3',
        'versions': ('1.1', '1.3'),
        'description': 'These conventions identify and define a list of NetCDF global attributes recommended for '
                       'describing a NetCDF dataset to discovery systems such as Digital Libraries. Software tools '
                       'will use these attributes for extracting metadata from datasets, and exporting to Dublin Core, '
                       'DIF, ADN, FGDC, ISO 19115 etc. metadata formats.',
    }

    DEFAULT_VERSION = '1.1'

    def setup(self, version):
        if version not in ACDD.ABOUT['versions']:
            return abort(
                400, 'Must specify valid version in the format "ACDD-version=x.x". '
                     f'Available versions are {ACDD.ABOUT["versions"]}'
            )

        self.version = version

        global_checks = self.add_group('Global Attributes', scope='globals')

        if version == '1.1':
            highly_recommended = global_checks.add_group('Highly Recommended')
            highly_recommended.add_checker(CheckExistence)
            highly_recommended.add_blueprints(
                [
                    {
                        'name': 'title',
                        'description': 'A short description of the dataset.',
                    },
                    {
                        'name': 'summary',
                        'description': 'A paragraph describing the dataset',
                    }
                ]
            )
            highly_recommended.add_blueprint(
                {
                    'name': 'keywords',
                    'description': 'A comma separated list of key words and phrases',
                }, CheckCommaSeparated
            )

            recommended = global_checks.add_group('Recommended')
            recommended.add_checker(CheckExistence)
            recommended.add_blueprints(
                [
                    {
                        'name': 'id',
                        'description': 'The combination of the "naming authority" and the "id" should be a globally '
                                       'unique identifier for the dataset.',
                    },
                    {
                        'name': 'naming_authority',
                        'description': 'The combination of the "naming authority" and the "id" should be a globally '
                                       'unique identifier for the dataset.',
                    },
                    {
                        'name': 'keywords_vocabulary',
                        'description': 'If you are following a guideline for the words/phrases in your "keywords" '
                                       'attribute, put the name of that guideline here.',
                    },
                    {
                        'name': 'creator_name',
                        'description': 'The data creator\'s name, URL, and email. The "institution" attribute will be '
                                       'used if the "creator_name" attribute does not exist.',
                    },
                    {
                        'name': 'creator_url',
                        'description': 'The data creator\'s name, URL, and email. The "institution" attribute will be '
                                       'used if the "creator_name" attribute does not exist.',
                    },
                    {
                        'name': 'creator_email',
                        'description': 'The data creator\'s name, URL, and email. The "institution" attribute will be '
                                       'used if the "creator_name" attribute does not exist.',
                    },
                    {
                        'name': 'history',
                        'description': 'Provides an audit trail for modifications to the original data.',
                    },
                    {
                        'name': 'comment',
                        'description': 'Miscellaneous information about the data.',
                    },
                    {
                        'name': 'institution',
                        'description': 'The data creator\'s name, URL, and email. The "institution" attribute will be '
                                       'used if the "creator_name" attribute does not exist.',
                    },
                    {
                        'name': 'project',
                        'description': 'The scientific project that produced the data.',
                    },
                    {
                        'name': 'processing_level',
                        'description': 'A textual description of the processing (or quality control) level of the data.'
                    },
                    {
                        'name': 'geospatial_lat_min',
                        'description': 'Describes a simple latitude/longitude bounding box. geospatial_lat_min '
                                       'specifies the southernmost latitude.',
                    },
                    {
                        'name': 'geospatial_lat_max',
                        'description': 'Describes a simple latitude/longitude bounding box. geospatial_lat_max '
                                       'specifies the northernmost latitude.',
                    },
                    {
                        'name': 'geospatial_lon_min',
                        'description': 'Describes a simple latitude/longitude bounding box. geospatial_lon_min '
                                       'specifies the westernmost longitude. The values of geospatial_lon_min and '
                                       'geospatial_lon_max reflect the actual longitude data values. Cases where '
                                       'geospatial_lon_min is greater than geospatial_lon_max indicate the bounding '
                                       'box extends from geospatial_lon_max, through the longitude range discontinuity '
                                       'meridian (either the antimeridian or Prime Meridian), to geospatial_lon_min.',
                    },
                    {
                        'name': 'geospatial_lon_max',
                        'description': 'Describes a simple latitude/longitude bounding box. geospatial_lon_max '
                                       'specifies the easternmost longitude. The values of geospatial_lon_min and '
                                       'geospatial_lon_max reflect the actual longitude data values. Cases where '
                                       'geospatial_lon_min is greater than geospatial_lon_max indicate the bounding '
                                       'box extends from geospatial_lon_max, through the longitude range discontinuity '
                                       'meridian (either the antimeridian or Prime Meridian), to geospatial_lon_min.',
                    },
                    {
                        'name': 'geospatial_vertical_min',
                        'description': 'Describes a simple vertical bounding box.',
                    },
                    {
                        'name': 'geospatial_vertical_max',
                        'description': 'Describes a simple vertical bounding box.',
                    },
                    {
                        'name': 'acknowledgement',
                        'description': 'A place to acknowledge various type of support for the project that produced '
                                       'this data.',
                    },
                    {
                        'name': 'standard_name_vocabulary',
                        'description': 'The name of the controlled vocabulary from which variable standard names are '
                                       'taken.',
                    },
                    {
                        'name': 'license',
                        'description': 'Describe the restrictions to data access and distribution.',
                    },
                    {
                        'name': 'time_coverage_resolution',
                        'description': 'Describes the temporal coverage of the data as a time range.',
                    },
                    {
                        'name': 'geospatial_bounds',
                        'description': 'Describes geospatial extent using any of the geometric objects (2D or 3D) '
                                       'supported by the Well-Known Text (WKT) format.',
                    }
                ]
            )
            recommended.add_blueprint(
                {
                    'name': 'cdm_data_type',
                    'possible_values': ['vector', 'grid', 'textTable', 'tin', 'stereoModel', 'video'],
                    'description': 'The THREDDS data type appropriate for this dataset',
                }, CheckPossibleValues
            )
            recommended.add_blueprints(
                [
                    {
                        'name': 'date_created',
                        'description': 'The date on which the data was created.',
                    },
                    {
                        'name': 'time_coverage_start',
                        'description': 'Describes the temporal coverage of the data as a time range.',
                    },
                    {
                        'name': 'time_coverage_end',
                        'description': 'Describes the temporal coverage of the data as a time range.',
                    }
                ], CheckISODatestuff
            )
            recommended.add_blueprint(
                {
                    'name': 'time_coverage_duration',
                    'description': 'Describes the temporal coverage of the data as a time range.',
                }, CheckISODuration
            )

            suggested = global_checks.add_group('Suggested')
            suggested.add_checker(CheckExistence)
            suggested.add_blueprints(
                [
                    {
                        'name': 'contributor_name',
                        'description': 'The name and role of any individuals or institutions that contributed to the '
                                       'creation of this data.',
                    },
                    {
                        'name': 'contributor_role',
                        'description': 'The name and role of any individuals or institutions that contributed to the '
                                       'creation of this data.',
                    },
                    {
                        'name': 'publisher_name',
                        'description': 'The publisher may be an individual or an institution.',
                    },
                    {
                        'name': 'publisher_url',
                        'description': 'The publisher may be an individual or an institution.',
                    },
                    {
                        'name': 'publisher_email',
                        'description': 'The publisher may be an individual or an institution.',
                    },
                    {
                        'name': 'date_modified',
                        'description': 'The date on which this data was last modified.',
                    },
                    {
                        'name': 'date_issued',
                        'description': 'The date on which this data was formally issued.',
                    },
                    {
                        'name': 'geospatial_lat_units',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_lat_resolution',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_lon_units',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_lon_resolution',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_vertical_units',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_vertical_resolution',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_vertical_positive',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    }
                ]
            )

            variable_attributes = self.add_group('Variable Attributes', scope='varattrs')
            variable_attributes.add_checker(CheckExistence)

            highly_recommended_varattrs = variable_attributes.add_group('Highly Recommended')
            highly_recommended_varattrs.add_blueprint(
                {
                    'name': 'long_name',
                    'description': 'A long descriptive name for the variable (not necessarily from a controlled '
                                   'vocabulary).',
                }
            )
            highly_recommended_varattrs.add_blueprint(
                {
                    'name': 'standard_name',
                    'description': 'A long descriptive name for the variable taken from a controlled vocabulary of '
                                   'variable names.',
                }, CheckStandardName
            )
            highly_recommended_varattrs.add_blueprint(
                {
                    'name': 'units',
                    'description': 'The units of the variables data values. This attributes\' value should be a valid '
                                   'udunits string.',
                }, CheckUDUnits
            )
            highly_recommended_varattrs.add_blueprint(
                {
                    'possible_values': ['image', 'thematicClassification', 'physicalMeasurement',
                                        'auxiliaryInformation', 'qualityInformation', 'referenceInformation',
                                        'modelResult', 'coordinate'],
                    'name': 'coverage_content_type',
                    'description': 'An ISO 19115-1 code to indicate the source of the data.',
                }, CheckPossibleValues
            )
        elif version == '1.3':
            highly_recommended = global_checks.add_group('Highly Recommended')
            highly_recommended.add_checker(CheckExistence)
            highly_recommended.add_blueprints(
                [
                    {
                        'name': 'title',
                        'description': 'A short phrase or sentence describing the dataset. In many discovery systems, '
                                       'the title will be displayed in the results list from a search, and therefore '
                                       'should be human readable and reasonable to display in a list of such names. '
                                       'This attribute is also recommended by the NetCDF Users Guide and the CF '
                                       'conventions.',
                    },
                    {
                        'name': 'summary',
                        'description': 'A paragraph describing the dataset, analogous to an abstract for a paper.',
                    }
                ]
            )
            highly_recommended.add_blueprint(
                {
                    'name': 'keywords',
                    'description': 'A comma-separated list of key words and/or phrases. Keywords may be common words '
                                   'or phrases, terms from a controlled vocabulary (GCMD is often used), or URIs for '
                                   'terms from a controlled vocabulary (see also "keywords_vocabulary" attribute).',
                }, CheckCommaSeparated
            )
            highly_recommended.add_blueprint(
                {
                    'name': 'Conventions',
                    'description': 'A comma-separated list of the conventions that are followed by the dataset. '
                                   'For files that follow this version of ACDD, include the string "ACDD-1.3". '
                                   '(This attribute is described in the NetCDF Users Guide.)',
                }, CheckCommaSeparated
            )

            recommended = global_checks.add_group('Recommended')
            recommended.add_checker(CheckExistence)
            recommended.add_blueprints(
                [
                    {
                        'name': 'id',
                        'description': 'An identifier for the data set, provided by and unique within its naming '
                                       'authority. The combination of the "naming authority" and the "id" should be '
                                       'globally unique, but the id can be globally unique by itself also. IDs can be '
                                       'URLs, URNs, DOIs, meaningful text strings, a local key, or any other unique '
                                       'string of characters. The id should not include white space characters.',
                    },
                    {
                        'name': 'naming_authority',
                        'description': 'The organization that provides the initial id (see above) for the dataset. '
                                       'The naming authority should be uniquely specified by this attribute. '
                                       'We recommend using reverse-DNS naming for the naming authority; '
                                       'URIs are also acceptable. Example: "edu.ucar.unidata".',
                    },
                    {
                        'name': 'history',
                        'description': 'Provides an audit trail for modifications to the original data.',
                    },
                    {
                        'name': 'source',
                        'description': 'The method of production of the original data. If it was model-generated, '
                                       'source should name the model and its version. If it is observational, '
                                       'source should characterize it. This attribute is defined in the CF '
                                       'Conventions. Examples: "temperature from CTD #1234"; "world model v.0.1".',
                    },
                    {
                        'name': 'processing_level',
                        'description': 'A textual description of the processing (or quality control) level of the data.'
                    },
                    {
                        'name': 'comment',
                        'description': 'Miscellaneous information about the data, not captured elsewhere. '
                                       'This attribute is defined in the CF Conventions.',
                    },
                    {
                        'name': 'acknowledgement',
                        'description': 'A place to acknowledge various type of support for the project that produced '
                                       'this data.',
                    },
                    {
                        'name': 'license',
                        'description': 'Describe the restrictions to data access and distribution.',
                    },
                    {
                        'name': 'standard_name_vocabulary',
                        'description': 'The name and version of the controlled vocabulary from which variable standard '
                                       'names are taken. (Values for any standard_name attribute must come from the CF '
                                       'Standard Names vocabulary for the data file or product to comply with CF.) '
                                       'Example: "CF Standard Name Table v27".',
                    },
                    {
                        'name': 'date_created',
                        'description': 'The date on which this version of the data was created. (Modification of '
                                       'values implies a new version, hence this would be assigned the date of the '
                                       'most recent values modification.) Metadata changes are not considered when '
                                       'assigning the date_created. The ISO 8601:2004 extended date format is '
                                       'recommended, as described in the Attribute Content Guidance section.',
                    },
                    {
                        'name': 'creator_name',
                        'description': 'The name of the person (or other creator type specified by the creator_type '
                                       'attribute) principally responsible for creating this data.',
                    },
                    {
                        'name': 'creator_email',
                        'description': 'The email address of the person (or other creator type specified by the '
                                       'creator_type attribute) principally responsible for creating this data.',
                    },
                    {
                        'name': 'creator_url',
                        'description': 'The URL of the person (or other creator type specified by the creator_type '
                                       'attribute) principally responsible for creating this data.',
                    },
                    {
                        'name': 'institution',
                        'description': 'The name of the institution principally responsible for originating this data. '
                                       'This attribute is recommended by the CF convention.',
                    },
                    {
                        'name': 'project',
                        'description': 'The name of the project(s) principally responsible for originating this data. '
                                       'Multiple projects can be separated by commas, as described under Attribute '
                                       'Content Guidelines. Examples: "PATMOS-X", "Extended Continental Shelf Project".'
                    },
                    {
                        'name': 'publisher_name',
                        'description': 'The name of the person (or other entity specified by the publisher_type '
                                       'attribute) responsible for publishing the data file or product to users, '
                                       'with its current metadata and format.',
                    },
                    {
                        'name': 'publisher_email',
                        'description': 'The email address of the person (or other entity specified by the '
                                       'publisher_type attribute) responsible for publishing the data file or product '
                                       'to users, with its current metadata and format.',
                    },
                    {
                        'name': 'publisher_url',
                        'description': 'The URL of the person (or other entity specified by the publisher_type '
                                       'attribute) responsible for publishing the data file or product to users, '
                                       'with its current metadata and format.',
                    },
                    {
                        'name': 'geospatial_bounds',
                        'description': "Describes the data's 2D or 3D geospatial extent in OGC's Well-Known Text (WKT) "
                                       "Geometry format (reference the OGC Simple Feature Access (SFA) specification). "
                                       "The meaning and order of values for each point's coordinates depends on the "
                                       "coordinate reference system (CRS). The ACDD default is 2D geometry in the "
                                       "EPSG:4326 coordinate reference system. The default may be overridden with "
                                       "geospatial_bounds_crs and geospatial_bounds_vertical_crs (see those "
                                       "attributes). EPSG:4326 coordinate values are latitude (decimal degrees_north) "
                                       "and longitude (decimal degrees_east), in that order. Longitude values in the "
                                       "default case are limited to the [-180, 180) range. Example: "
                                       "'POLYGON ((40.26 -111.29, 41.26 -111.29, 41.26 -110.29, 40.26 -110.29, 40.26 "
                                       "-111.29))'.",
                    },
                    {
                        'name': 'geospatial_bounds_crs',
                        'description': "The coordinate reference system (CRS) of the point coordinates in the "
                                       "geospatial_bounds attribute. This CRS may be 2-dimensional or 3-dimensional, "
                                       "but together with geospatial_bounds_vertical_crs, if that attribute is "
                                       "supplied, must match the dimensionality, order, and meaning of point "
                                       "coordinate values in the geospatial_bounds attribute. If "
                                       "geospatial_bounds_vertical_crs is also present then this attribute must only "
                                       "specify a 2D CRS. EPSG CRSs are strongly recommended. If this attribute is not "
                                       "specified, the CRS is assumed to be EPSG:4326. Examples: 'EPSG:4979' "
                                       "(the 3D WGS84 CRS), 'EPSG:4047'.",
                    },
                    {
                        'name': 'geospatial_bounds_vertical_crs',
                        'description': "The vertical coordinate reference system (CRS) for the Z axis of the point "
                                       "coordinates in the geospatial_bounds attribute. This attribute cannot be used "
                                       "if the CRS in geospatial_bounds_crs is 3-dimensional; to use this attribute, "
                                       "geospatial_bounds_crs must exist and specify a 2D CRS. EPSG CRSs are strongly "
                                       "recommended. There is no default for this attribute when not specified. "
                                       "Examples: 'EPSG:5829' (instantaneous height above sea level), "
                                       "'EPSG:5831' (instantaneous depth below sea level), or 'EPSG:5703' "
                                       "(NAVD88 height).",
                    },
                    {
                        'name': 'geospatial_lat_min',
                        'description': 'Describes a simple lower latitude limit; may be part of a 2- or 3-dimensional '
                                       'bounding region. Geospatial_lat_min specifies the southernmost latitude '
                                       'covered by the dataset.',
                    },
                    {
                        'name': 'geospatial_lat_max',
                        'description': 'Describes a simple upper latitude limit; may be part of a 2- or 3-dimensional '
                                       'bounding region. Geospatial_lat_max specifies the northernmost latitude '
                                       'covered by the dataset.',
                    },
                    {
                        'name': 'geospatial_lon_min',
                        'description': 'Describes a simple longitude limit; may be part of a 2- or 3-dimensional '
                                       'bounding region. geospatial_lon_min specifies the westernmost longitude '
                                       'covered by the dataset. See also geospatial_lon_max.',
                    },
                    {
                        'name': 'geospatial_lon_max',
                        'description': 'Describes a simple longitude limit; may be part of a 2- or 3-dimensional '
                                       'bounding region. geospatial_lon_max specifies the easternmost longitude '
                                       'covered by the dataset. Cases where geospatial_lon_min is greater than '
                                       'geospatial_lon_max indicate the bounding box extends from geospatial_lon_max, '
                                       'through the longitude range discontinuity meridian (either the antimeridian '
                                       'for -180:180 values, or Prime Meridian for 0:360 values), to '
                                       'geospatial_lon_min; for example, geospatial_lon_min=170 and '
                                       'geospatial_lon_max=-175 incorporates 15 degrees of longitude (ranges 170 to '
                                       '180 and -180 to -175).',
                    },
                    {
                        'name': 'geospatial_vertical_min',
                        'description': 'Describes the numerically smaller vertical limit; may be part of a 2- or '
                                       '3-dimensional bounding region. See geospatial_vertical_positive and '
                                       'geospatial_vertical_units.',
                    },
                    {
                        'name': 'geospatial_vertical_max',
                        'description': 'Describes the numerically larger vertical limit; may be part of a 2- or '
                                       '3-dimensional bounding region. See geospatial_vertical_positive and '
                                       'geospatial_vertical_units.',
                    },
                    {
                        'name': 'geospatial_vertical_positive',
                        'description': "One of 'up' or 'down'. If up, vertical values are interpreted as 'altitude', "
                                       "with negative values corresponding to below the reference datum "
                                       "(e.g., under water). If down, vertical values are interpreted as 'depth', "
                                       "positive values correspond to below the reference datum. Note that if "
                                       "geospatial_vertical_positive is down ('depth' orientation), the "
                                       "geospatial_vertical_min attribute specifies the data's vertical location "
                                       "furthest from the earth's center, and the geospatial_vertical_max attribute "
                                       "specifies the location closest to the earth's center.",
                    },
                    {
                        'name': 'geospatial_vertical_positive',
                        'description': "One of 'up' or 'down'. If up, vertical values are interpreted as 'altitude', "
                                       "with negative values corresponding to below the reference datum "
                                       "(e.g., under water). If down, vertical values are interpreted as 'depth', "
                                       "positive values correspond to below the reference datum. Note that if "
                                       "geospatial_vertical_positive is down ('depth' orientation), the "
                                       "geospatial_vertical_min attribute specifies the data's vertical location "
                                       "furthest from the earth's center, and the geospatial_vertical_max attribute "
                                       "specifies the location closest to the earth's center.",
                    },
                    {
                        'name': 'time_coverage_resolution',
                        'description': 'Describes the targeted time period between each value in the data set. '
                                       'Use ISO 8601:2004 duration format, preferably the extended format as '
                                       'recommended in the Attribute Content Guidance section.',
                    }
                ]
            )

            recommended.add_blueprints(
                [
                    {
                        'name': 'time_coverage_start',
                        'description': 'Describes the time of the first data point in the data set. Use the '
                                       'ISO 8601:2004 date format, preferably the extended format as recommended in '
                                       'the Attribute Content Guidance section.',
                    },
                    {
                        'name': 'time_coverage_end',
                        'description': 'Describes the time of the last data point in the data set. Use '
                                       'ISO 8601:2004 date format, preferably the extended format as recommended in '
                                       'the Attribute Content Guidance section.',
                    }
                ], CheckISODatestuff
            )

            recommended.add_blueprint(
                {
                    'name': 'time_coverage_duration',
                    'description': 'Describes the duration of the data set. Use ISO 8601:2004 duration format, '
                                   'preferably the extended format as recommended in the Attribute Content '
                                   'Guidance section.',
                }, CheckISODuration
            )

            suggested = global_checks.add_group('Suggested')
            suggested.add_checker(CheckExistence)
            suggested.add_blueprint(
                {
                    'name': 'cdm_data_type',
                    'possible_values': ['Grid', 'Image', 'Point', 'Radial', 'Station', 'Swath', 'Trajectory'],
                    'description': "The data type, as derived from Unidata's Common Data Model Scientific Data types "
                                   "and understood by THREDDS. (This is a THREDDS 'dataType', and is different from "
                                   "the CF NetCDF attribute 'featureType', which indicates a Discrete Sampling "
                                   "Geometry file in CF.)",
                }, CheckPossibleValues
            )

            suggested.add_blueprints(
                [
                    {
                        'name': 'creator_type',
                        'description': "Specifies type of creator with one of the following: 'person', 'group', "
                                       "'institution', or 'position'. If this attribute is not specified, the creator "
                                       "is assumed to be a person.",
                    },
                    {
                        'name': 'creator_institution',
                        'description': "The institution of the creator; should uniquely identify the creator's "
                                       "institution. This attribute's value should be specified even if it matches the "
                                       "value of publisher_institution, or if creator_type is institution.",
                    },
                    {
                        'name': 'publisher_type',
                        'description': 'The institution that presented the data file or equivalent product to users; '
                                       'should uniquely identify the institution. If publisher_type is institution, '
                                       'this should have the same value as publisher_name.',
                    },
                    {
                        'name': 'program',
                        'description': "The overarching program(s) of which the dataset is a part. A program consists "
                                       "of a set (or portfolio) of related and possibly interdependent projects that "
                                       "meet an overarching objective. Examples: 'GHRSST', 'NOAA CDR', 'NASA EOS', "
                                       "'JPSS', 'GOES-R'.",
                    },
                    {
                        'name': 'contributor_name',
                        'description': 'The name of any individuals, projects, or institutions that contributed to the '
                                       'creation of this data. May be presented as free text, or in a structured '
                                       'format compatible with conversion to ncML (e.g., insensitive to changes in '
                                       'whitespace, including end-of-line characters).',
                    },
                    {
                        'name': 'contributor_role',
                        'description': 'The role of any individuals, projects, or institutions that contributed to the '
                                       'creation of this data. May be presented as free text, or in a structured '
                                       'format compatible with conversion to ncML (e.g., insensitive to changes in '
                                       'whitespace, including end-of-line characters). Multiple roles should be '
                                       'presented in the same order and number as the names in contributor_names.',
                    },
                    {
                        'name': 'geospatial_lat_units',
                        'description': 'Units for the latitude axis described in "geospatial_lat_min" and '
                                       '"geospatial_lat_max" attributes. These are presumed to be "degree_north"; '
                                       'other options from udunits may be specified instead.',
                    },
                    {
                        'name': 'geospatial_lat_resolution',
                        'description': "Information about the targeted spacing of points in latitude. Recommend "
                                       "describing resolution as a number value followed by the units. "
                                       "Examples: '100 meters', '0.1 degree'",
                    },
                    {
                        'name': 'geospatial_lon_units',
                        'description': 'Units for the longitude axis described in "geospatial_lon_min" and '
                                       '"geospatial_lon_max" attributes. These are presumed to be "degree_east"; '
                                       'other options from udunits may be specified instead.',
                    },
                    {
                        'name': 'geospatial_lon_resolution',
                        'description': 'Units for the vertical axis described in "geospatial_vertical_min" and '
                                       '"geospatial_vertical_max" attributes. The default is EPSG:4979 '
                                       '(height above the ellipsoid, in meters); other vertical coordinate reference '
                                       'systems may be specified. Note that the common oceanographic practice of using '
                                       'pressure for a vertical coordinate, while not strictly a depth, can be '
                                       'specified using the unit bar. Examples: "EPSG:5829" (instantaneous height '
                                       'above sea level), "EPSG:5831" (instantaneous depth below sea level).',
                    },
                    {
                        'name': 'product_version',
                        'description': 'Version identifier of the data file or product as assigned by the data '
                                       'creator. For example, a new algorithm or methodology could result in a new '
                                       'product_version.',
                    },
                    {
                        'name': 'keywords_vocabulary',
                        'description': 'If you are using a controlled vocabulary for the words/phrases in your '
                                       '"keywords" attribute, this is the unique name or identifier of the vocabulary '
                                       'from which keywords are taken. If more than one keyword vocabulary is used, '
                                       'each may be presented with a prefix and a following comma, so that keywords '
                                       'may optionally be prefixed with the controlled vocabulary key. '
                                       'Example: "GCMD:GCMD Keywords, CF:NetCDF COARDS Climate and Forecast Standard '
                                       'Names".',
                    },
                    {
                        'name': 'platform',
                        'description': 'Name of the platform(s) that supported the sensor data used to create this '
                                       'data set or product. Platforms can be of any type, including satellite, ship, '
                                       'station, aircraft or other. Indicate controlled vocabulary used in '
                                       'platform_vocabulary.',
                    },
                    {
                        'name': 'platform_vocabulary',
                        'description': 'Controlled vocabulary for the names used in the "platform" attribute.',
                    },
                    {
                        'name': 'instrument',
                        'description': 'Name of the contributing instrument(s) or sensor(s) used to create this data '
                                       'set or product. Indicate controlled vocabulary used in instrument_vocabulary.',
                    },
                    {
                        'name': 'instrument_vocabulary',
                        'description': 'Controlled vocabulary for the names used in the "instrument" attribute.',
                    },
                    {
                        'name': 'metadata_link',
                        'description': 'A URL that gives the location of more complete metadata. A persistent URL is '
                                       'recommended for this attribute.',
                    },
                    {
                        'name': 'references',
                        'description': 'Published or web-based references that describe the data or methods used to '
                                       'produce it. Recommend URIs (such as a URL or DOI) for papers or other '
                                       'references. This attribute is defined in the CF conventions.',
                    },
                    {
                        'name': 'contributor_name',
                        'description': 'The name and role of any individuals or institutions that contributed to the '
                                       'creation of this data.',
                    },
                    {
                        'name': 'contributor_role',
                        'description': 'The name and role of any individuals or institutions that contributed to the '
                                       'creation of this data.',
                    },
                    {
                        'name': 'geospatial_lat_units',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_lat_resolution',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_lon_units',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_lon_resolution',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_vertical_units',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    },
                    {
                        'name': 'geospatial_vertical_resolution',
                        'description': 'Further refinement of the geospatial bounding box can be provided by using '
                                       'these units and resolution attributes.',
                    }
                ]
            )

            suggested.add_blueprints(
                [
                    {
                        'name': 'date_modified',
                        'description': 'The date on which the data was last modified. Note that this applies just to '
                                       'the data, not the metadata. The ISO 8601:2004 extended date format is '
                                       'recommended, as described in the Attributes Content Guidance section.',
                    },
                    {
                        'name': 'date_issued',
                        'description': 'The date on which this data (including all modifications) was formally issued '
                                       '(i.e., made available to a wider audience). Note that these apply just to the '
                                       'data, not the metadata. The ISO 8601:2004 extended date format is recommended, '
                                       'as described in the Attributes Content Guidance section.',
                    },
                    {
                        'name': 'date_metadata_modified',
                        'description': 'The date on which the metadata was last modified. The ISO 8601:2004 extended '
                                       'date format is recommended, as described in the Attributes Content Guidance '
                                       'section.',
                    }
                ], CheckISODatestuff
            )

            variable_attributes = self.add_group('Variable Attributes', scope='varattrs')
            variable_attributes.add_checker(CheckExistence)

            highly_recommended_varattrs = variable_attributes.add_group('Highly Recommended')
            highly_recommended_varattrs.add_blueprint(
                {
                    'name': 'long_name',
                    'description': 'A long descriptive name for the variable (not necessarily from a controlled '
                                   'vocabulary). This attribute is recommended by the NetCDF Users Guide, the COARDS '
                                   'convention, and the CF convention.',
                }
            )
            highly_recommended_varattrs.add_blueprint(
                {
                    'name': 'standard_name',
                    'description': 'A long descriptive name for the variable taken from a controlled vocabulary of '
                                   'variable names. We recommend using the CF convention and the variable names from '
                                   'the CF standard name table. This attribute is recommended by the CF convention.',
                }, CheckStandardName
            )
            highly_recommended_varattrs.add_blueprint(
                {
                    'name': 'units',
                    'description': 'The units of the variable\'s data values. This attribute value should be a valid '
                                   'udunits string. The "units" attribute is recommended by the NetCDF Users Guide, '
                                   'the COARDS convention, and the CF convention.',
                }, CheckUDUnits
            )
            highly_recommended_varattrs.add_blueprint(
                {
                    'possible_values': ['image', 'thematicClassification', 'physicalMeasurement',
                                        'auxiliaryInformation', 'qualityInformation', 'referenceInformation',
                                        'modelResult', 'coordinate'],
                    'name': 'coverage_content_type',
                    'description': 'An ISO 19115-1 code to indicate the source of the data.',
                }, CheckPossibleValues
            )

            deprecated = global_checks.add_group('Deprecated')

            deprecated.add_blueprint(
                {
                    'name': 'Metadata_Convention',
                    'description': "removed in favor of 'Conventions'",
                }, CheckDeprecated
            )

        return self
