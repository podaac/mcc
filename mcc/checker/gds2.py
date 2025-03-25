"""
=======
gds2.py
=======

CheckSuite definition for GDS2 L2P, L3, L4 data.

TODO: what do 'none' mean in varattrs?
TODO: cleanup setup() to be less repetitive
TODO: add filename validity check
TODO: better descriptions (and show them!)
TODO: create actual checks for the possibly required stuff (or at least add descriptions)
TODO: do not flunk the test if not required
TODO: use dicts instead of 2-dimensional tuples -- more descriptive
"""

from flask import abort

from .base import CheckSuite
from .checkers import CheckExistence, CheckTypes


class GDS2(CheckSuite):
    ABOUT = {
        'name': 'Group for High Resolution Sea Surface Temperature Data Specification, Version 2.1',
        'short_name': 'GDS2',
        'url': 'https://zenodo.org/records/6984989',
        'versions': ('Version 2.1, Revision 0',),
        'description': 'The GHRSST Data Specification (GDS) Version 2.1 is a technical specification of GHRSST '
                       'products and services.',
        'options': ('L2P', 'L3', 'L4'),
    }

    DEFAULT_VERSION = 'L2P'

    REQUIRED_GLOBALS_STRINGS = (
        'Conventions', 'title', 'summary', 'references', 'institution', 'history', 'comment', 'license', 'id',
        'naming_authority', 'product_version', 'uuid', 'gds_version_id', 'netcdf_version_id', 'date_created',
        'spatial_resolution', 'start_time', 'time_coverage_start', 'stop_time', 'time_coverage_end', 'source',
        'platform', 'sensor', 'Metadata_Conventions', 'metadata_link', 'keywords', 'keywords_vocabulary',
        'standard_name_vocabulary', 'geospatial_lat_units', 'geospatial_lon_units', 'acknowledgment', 'creator_name',
        'creator_email', 'creator_url', 'project', 'publisher_name', 'publisher_url', 'publisher_email',
        'processing_level', 'cdm_data_type',
    )

    REQUIRED_GLOBALS_FLOATS = (
        'northernmost_latitude', 'southernmost_latitude', 'easternmost_longitude', 'westernmost_longitude',
        'geospatial_lat_resolution', 'geospatial_lon_resolution',
    )

    REQUIRED_GLOBALS_INTS = (
        'file_quality_level',
    )

    L2P_variables = (
        (
            {'name': 'lat', 'priority': 'required', 'type': 'float'},
            {'name': 'lon', 'priority': 'required', 'type': 'float'},
            {'name': 'time', 'priority': 'required', 'type': 'long'},
            {'name': 'sea_surface_temperature', 'priority': 'Required ', 'type': 'short'},
            {'name': 'sst_dtime', 'priority': 'required ', 'type': 'short'},
            {'name': 'sses_bias', 'priority': 'required', 'type': 'byte'},
            {'name': 'sses_standard_deviation', 'priority': 'required', 'type': 'byte'},
            {'name': 'dt_analysis', 'priority': 'required', 'type': 'byte'},
            {'name': 'l2p_flags', 'priority': 'required', 'type': 'short'},
            {'name': 'quality_level', 'priority': 'required', 'type': 'byte'},
            {'name': 'wind_speed', 'priority': 'required', 'type': 'byte'},
        ),
        (
            {'name': 'wind_speed_dtime_from_sst', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'sources_of_wind_speed', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'sea_ice_fraction', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'sea_ice_fraction_dtime_from_sst', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'sources_of_sea_ice_fraction', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'aerosol_dynamic_indicator', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'adi_dtime_from_sst', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'sources_of_adi', 'priority': 'maybe', 'type': 'byte'},
            {'name': 'ssi_dtime_from_sst', 'priority': 'maybe', 'type': 'byte'},
        ),
        (
            {'name': 'satellite_zenith_angle', 'priority': 'optional', 'type': 'byte'},
            {'name': 'solar_zenith_angle', 'priority': 'optional', 'type': 'byte'},
            {'name': 'surface_solar_irradiance', 'priority': 'optional', 'type': 'byte'},
            {'name': 'sources_of_ssi', 'priority': 'optional', 'type': 'byte'},
        ),
    )

    L2P_varattrs = (
        (
            {'priority': 'required', 'type': ('string',), 'name': 'long_name'},
            {'priority': 'required', 'type': ('string',), 'name': 'comment'},
        ),
        (
            {'priority': 'maybe',
             'variables': ('sea_surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation',
                           'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst', 'sources_of_wind_speed',
                           'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst',  'sources_of_sea_ice_fraction',
                           'aerosol_dynamic_indicator', 'adi_dtime_from_sst', 'sources_of_adi', 'quality_level',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'sources_of_ssi'),
             'type': ('byte', 'short', 'float'),
             'name': '_FillValue'},
            {'priority': 'maybe',
             'variables': ('time', 'lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst', 'aerosol_dynamic_indicator',
                           'adi_dtime_from_sst', 'satellite_zenith_angle', 'solar_zenith_angle',
                           'surface_solar_irradiance', 'ssi_dtime_from_sst'),
             'type': ('string',),
             'name': 'units'},
            {'priority': 'maybe',
             'variables': ('sea_surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation',
                           'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst', 'sea_ice_fraction',
                           'sea_ice_fraction_dtime_from_sst', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           '|satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst'),
             'type': ('float',),
             'name': 'scale_factor'},
            {'priority': 'maybe',
             'variables': ('surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation', 'dt_analysis',
                           'wind_speed', 'wind_speed_dtime_from_sst', 'sea_ice_fraction',
                           'sea_ice_fraction_dtime_from_sst', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst'),
             'type': ('float',),
             'name': 'add_offset'},
            {'priority': 'maybe',
             'variables': ('lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sources_of_wind_speed', 'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst',
                           'sources_of_sea_ice_fraction', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'sources_of_adi', 'l2p_flags', 'quality_level', 'satellite_zenith_angle',
                           'solar_zenith_angle', 'surface_solar_irradiance', 'ssi_dtime_from_sst',
                           'sources_of_ssi'),
             'type': ('byte', 'short', 'float'),
             'name': 'valid_min'},
            {'priority': 'maybe',
             'variables': ('lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sources_of_wind_speed', 'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst',
                           'sources_of_sea_ice_fraction', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'sources_of_adi', 'l2p_flags', 'quality_level', 'satellite_zenith_angle',
                           'solar_zenith_angle', 'surface_solar_irradiance', 'ssi_dtime_from_sst',
                           'sources_of_ssi'),
             'type': ('byte', 'short', 'float'),
             'name': 'valid_max'},
            {'priority': 'maybe',
             'variables': ('time', 'lat', 'lon', 'sea_surface_temperature', 'analysed_sst', 'sea_ice_fraction',
                           'wind_speed'),
             'type': ('string',),
             'name': 'standard_name'},
            {'priority': 'maybe',
             'variables': ('sea_ice_fraction', 'wind_speed', 'aerosol_dynamic_indicator', 'surface_solar_irradiance'),
             'type': ('string',),
             'name': 'source'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'reference'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'positive'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'grid_mapping'},
            {'priority': 'maybe',
             'variables': ('sea_surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation',
                           'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst', 'sources_of_wind_speed',
                           'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst', 'sources_of_sea_ice_fraction',
                           'aerosol_dynamic_indicator', 'adi_dtime_from_sst', 'sources_of_adi', 'l2p_flags',
                           'quality_level', 'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'sources_of_ssi'),
             'type': ('string',),
             'name': 'coordinates'},
            {'priority': 'maybe',
             'variables': ('quality_level', 'l2p_flags', 'sources_of_wind_speed', 'sources_of_sea_ice_fraction',
                           'sources_of_adi', 'sources_of_ssi'),
             'type': ('string',),
             'name': 'flag_meanings'},
            {'priority': 'maybe',
             'variables': ('quality_level', 'sources_of_wind_speed', 'sources_of_sea_ice_fraction', 'sources_of_adi',
                           'sources_of_ssi'),
             'type': ('byte', 'short'),
             'name': 'flag_values'},
            {'priority': 'maybe', 'variables': ('l2p_flags',), 'type': ('short',), 'name': 'flag_masks'},
            {'priority': 'maybe', 'variables': ('wind_speed',), 'type': ('string',), 'name': 'height'},
        ),
        (
            {'priority': 'optional', 'variables': ('time',), 'type': ('string',), 'name': 'axis'},
            {'priority': 'optional', 'variables': ('sea_surface_temperature',), 'type': ('string',), 'name': 'depth'},
            {'priority': 'optional',
             'variables': ('sea_ice_fraction', 'wind_speed', 'aerosol_dynamic_indicator', 'surface_solar_irradiance'),
             'type': ('float',),
             'name': 'time_offset'},
        )
    )

    L3_variables = (
        (
            {'name': 'lat', 'type': 'float', 'priority': 'required'},
            {'name': 'lon', 'type': 'float', 'priority': 'required'},
            {'name': 'time', 'type': 'long', 'priority': 'required'},
            {'name': 'sea_surface_temperature', 'type': 'short', 'priority': 'required'},
            {'name': 'sst_dtime', 'type': 'long', 'priority': 'required'},
            {'name': 'sses_bias', 'type': 'byte', 'priority': 'required'},
            {'name': 'sses_standard_deviation', 'type': 'byte', 'priority': 'required'},
            {'name': 'quality_level', 'type': 'byte', 'priority': 'required'},
        ),
        (
            {'name': 'dt_analysis', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'l2p_flags', 'type': 'short', 'priority': 'maybe'},
            {'name': 'wind_speed', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'wind_speed_dtime_from_sst', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'sources_of_wind_speed', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'sea_ice_fraction', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'sea_ice_fraction_dtime_from_sst', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'sources_of_sea_ice_fraction', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'aerosol_dynamic_indicator', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'adi_dtime_from_sst', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'sources_of_adi', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'ssi_dtime_from_sst', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'adjusted_sea_surface_temperature', 'type': 'short', 'priority': 'maybe'},
            {'name': 'adjusted_standard_deviation_error', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'bias_to_reference_sst', 'type': 'short', 'priority': 'maybe'},
            {'name': 'standard_deviation_to_reference_sst', 'type': 'byte', 'priority': 'maybe'},
            {'name': 'sources_of_sst', 'type': 'byte', 'priority': 'maybe'},
        ),
        (
            {'name': 'satellite_zenith_angle', 'type': 'byte', 'priority': 'optional'},
            {'name': 'solar_zenith_angle', 'type': 'byte', 'priority': 'optional'},
            {'name': 'surface_solar_irradiance', 'type': 'byte', 'priority': 'optional'},
            {'name': 'sources_of_ssi', 'type': 'byte', 'priority': 'optional'},
            {'name': 'or_latitude', 'type': 'short', 'priority': 'optional'},
            {'name': 'or_longitude', 'type': 'short', 'priority': 'optional'},
            {'name': 'or_number_of_pixels', 'type': 'short', 'priority': 'optional'},
            {'name': 'sum_square_sst', 'type': 'float', 'priority': 'optional'},
            {'name': 'sum_sst', 'type': 'float', 'priority': 'optional'},
        ),
    )

    L3_varattrs = (
        (
            {'priority': 'required', 'type': ('string',), 'name': 'long_name'},
            {'priority': 'required', 'type': ('string',), 'name': 'comment'},
        ),
        (
            {'priority': 'maybe',
             'variables': ('sea_surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation',
                           'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst', 'sources_of_wind_speed',
                           'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst', 'sources_of_sea_ice_fraction',
                           'aerosol_dynamic_indicator', 'adi_dtime_from_sst', 'sources_of_adi', 'quality_level',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'sources_of_ssi', 'or_latitude', 'or_longitude',
                           'or_number_of_pixels', 'sum_square_sst', 'adjusted_sea_surface_temperature',
                           'adjusted_standard_deviation_error', 'bias_to_reference_sst',
                           'standard_deviation_to_reference_sst', 'sources_of_ss'),
             'type': ('byte', 'short', 'float'),
             'name': '_FillValue'},
            {'priority': 'maybe',
             'variables': ('time', 'lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst', '|aerosol_dynamic_indicator',
                           'adi_dtime_from_sst', 'satellite_zenith_angle', 'solar_zenith_angle',
                           'surface_solar_irradiance', 'ssi_dtime_from_sst', 'or_latitude', 'or_longitude',
                           'or_number_of_pixels', 'sum_square_sst', 'adjusted_sea_surface_temperature',
                           'adjusted_standard_deviation_error', 'bias_to_reference_sst',
                           'standard_deviation_to_reference_sst'), 'type': ('string',), 'name': 'units'},
            {'priority': 'maybe',
             'variables': ('sea_surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation',
                           'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst', 'sea_ice_fraction',
                           'sea_ice_fraction_dtime_from_sst', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'or_latitude', 'or_longitude', 'or_number_of_pixels',
                           'sum_square_sst', 'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst'),
             'type': ('float',),
             'name': 'scale_factor'},
            {'priority': 'maybe',
             'variables': ('surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation', 'dt_analysis',
                           'wind_speed', 'wind_speed_dtime_from_sst', 'sea_ice_fraction',
                           'sea_ice_fraction_dtime_from_sst', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'or_latitude', 'or_longitude', 'or_number_of_pixels',
                           'sum_square_sst', 'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst'),
             'type': ('float',),
             'name': 'add_offset'},
            {'priority': 'maybe',
             'variables': ('lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sources_of_wind_speed', 'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst',
                           'sources_of_sea_ice_fraction', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'sources_of_adi', 'l2p_flags', 'quality_level', 'satellite_zenith_angle',
                           'solar_zenith_angle', 'surface_solar_irradiance', 'ssi_dtime_from_sst', 'sources_of_ssi',
                           'or_latitude', 'or_longitude', 'or_number_of_pixels', 'sum_square_sst',
                           'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst', 'sources_of_ss'),
             'type': ('byte', 'short', 'float'),
             'name': 'valid_min'},
            {'priority': 'maybe',
             'variables': ('lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sources_of_wind_speed', 'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst',
                           'sources_of_sea_ice_fraction', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'sources_of_adi', 'l2p_flags', 'quality_level', 'satellite_zenith_angle',
                           'solar_zenith_angle', 'surface_solar_irradiance', 'ssi_dtime_from_sst', 'sources_of_ssi',
                           'or_latitude', 'or_longitude', 'or_number_of_pixels', 'sum_square_sst',
                           'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst', 'sources_of_ss'),
             'type': ('byte', 'short', 'float'),
             'name': 'valid_max'},
            {'priority': 'maybe',
             'variables': ('time', 'lat', 'lon', 'sea_surface_temperature', 'analysed_sst', 'sea_ice_fraction',
                           'wind_speed', 'or_latitude', 'or_longitude', 'adjusted_sea_surface_temperature'),
             'type': ('string',),
             'name': 'standard_name'},
            {'priority': 'maybe',
             'variables': ('sea_ice_fraction', 'wind_speed', 'aerosol_dynamic_indicator', 'surface_solar_irradiance'),
             'type': ('string',),
             'name': 'source'},
            {'priority': 'maybe',
             'variables': ('adjusted_sea_surface_temperature',),
             'type': ('string',),
             'name': 'reference'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'positive'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'grid_mapping'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'coordinates'},
            {'priority': 'maybe',
             'variables': ('quality_level', 'l2p_flags', 'sources_of_wind_speed', 'sources_of_sea_ice_fraction',
                           'sources_of_adi', 'sources_of_ssi'),
             'type': ('string',),
             'name': 'flag_meanings'},
            {'priority': 'maybe',
             'variables': ('quality_level', 'sources_of_wind_speed', 'sources_of_sea_ice_fraction', 'sources_of_adi',
                           'sources_of_ssi'),
             'type': ('byte', 'short'),
             'name': 'flag_values'},
            {'priority': 'maybe', 'variables': ('l2p_flags',), 'type': ('short',), 'name': 'flag_masks'},
            {'priority': 'maybe', 'variables': ('wind_speed',), 'type': ('string',), 'name': 'height'},
        ),
        (
            {'priority': 'optional', 'variables': ('time', 'lon', 'lat'), 'type': ('string',), 'name': 'axis'},
            {'priority': 'optional',
             'variables': ('sea_surface_temperature', 'adjusted_sea_surface_temperature'),
             'type': ('string',),
             'name': 'depth'},
            {'priority': 'optional',
             'variables': ('sea_ice_fraction', 'wind_speed', 'aerosol_dynamic_indicator', 'surface_solar_irradiance'),
             'type': ('float',),
             'name': 'time_offset'},
        )
    )

    L4_variables = (
        (
            {'name': 'lat', 'type': 'float', 'priority': 'required'},
            {'name': 'lon', 'type': 'float', 'priority': 'required'},
            {'name': 'time', 'type': 'long', 'priority': 'required'},
            {'name': 'analysed_sst', 'type': 'short', 'priority': 'required'},
            {'name': 'analysis_error', 'type': 'short', 'priority': 'required'},
            {'name': 'mask', 'type': 'byte', 'priority': 'required'},
            {'name': 'sea_ice_fraction', 'type': 'byte', 'priority': 'required'},
        ), (
            {'name': 'sea_ice_fraction_error', 'type': 'byte', 'priority': 'optional'},
        ),
    )

    L4_varattrs = (
        (
            {'priority': 'required', 'type': ('string',), 'name': 'long_name'},
            {'priority': 'required', 'type': ('string',), 'name': 'comment'},
        ), (
            {'priority': 'maybe',
             'variables': ('sea_surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation',
                           'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst', 'sources_of_wind_speed',
                           'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst', 'sources_of_sea_ice_fraction',
                           'aerosol_dynamic_indicator', 'adi_dtime_from_sst', 'sources_of_adi', 'quality_level',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'sources_of_ssi', 'or_latitude', 'or_longitude',
                           'or_number_of_pixels', 'sum_square_sst', 'adjusted_sea_surface_temperature',
                           'adjusted_standard_deviation_error', 'bias_to_reference_sst',
                           'standard_deviation_to_reference_sst', 'sources_of_ss'),
             'type': ('byte', 'short', 'float'),
             'name': '_FillValue'},
            {'priority': 'maybe',
             'variables': ('time', 'lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst', '|aerosol_dynamic_indicator',
                           'adi_dtime_from_sst', 'satellite_zenith_angle', 'solar_zenith_angle',
                           'surface_solar_irradiance', 'ssi_dtime_from_sst', 'or_latitude', 'or_longitude',
                           'or_number_of_pixels', 'sum_square_sst', 'adjusted_sea_surface_temperature',
                           'adjusted_standard_deviation_error', 'bias_to_reference_sst',
                           'standard_deviation_to_reference_sst'),
             'type': ('string',),
             'name': 'units'},
            {'priority': 'maybe',
             'variables': ('sea_surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation',
                           'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst', 'sea_ice_fraction',
                           'sea_ice_fraction_dtime_from_sst', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'or_latitude', 'or_longitude', 'or_number_of_pixels',
                           'sum_square_sst', 'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst'),
             'type': ('float',),
             'name': 'scale_factor'},
            {'priority': 'maybe',
             'variables': ('surface_temperature', 'sst_dtime', 'sses_bias', 'sses_standard_deviation', 'dt_analysis',
                           'wind_speed', 'wind_speed_dtime_from_sst', 'sea_ice_fraction',
                           'sea_ice_fraction_dtime_from_sst', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'satellite_zenith_angle', 'solar_zenith_angle', 'surface_solar_irradiance',
                           'ssi_dtime_from_sst', 'or_latitude', 'or_longitude', 'or_number_of_pixels',
                           'sum_square_sst', 'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst'),
             'type': ('float',),
             'name': 'add_offset'},
            {'priority': 'maybe',
             'variables': ('lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sources_of_wind_speed', 'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst',
                           'sources_of_sea_ice_fraction', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'sources_of_adi', 'l2p_flags', 'quality_level', 'satellite_zenith_angle',
                           'solar_zenith_angle', 'surface_solar_irradiance', 'ssi_dtime_from_sst', 'sources_of_ssi',
                           'or_latitude', 'or_longitude', 'or_number_of_pixels', 'sum_square_sst',
                           'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst', 'sources_of_ss'),
             'type': ('byte', 'short', 'float'),
             'name': 'valid_min'},
            {'priority': 'maybe',
             'variables': ('lon', 'lat', 'sea_surface_temperature', 'sst_dtime', 'sses_bias',
                           'sses_standard_deviation', 'dt_analysis', 'wind_speed', 'wind_speed_dtime_from_sst',
                           'sources_of_wind_speed', 'sea_ice_fraction', 'sea_ice_fraction_dtime_from_sst',
                           'sources_of_sea_ice_fraction', 'aerosol_dynamic_indicator', 'adi_dtime_from_sst',
                           'sources_of_adi', 'l2p_flags', 'quality_level', 'satellite_zenith_angle',
                           'solar_zenith_angle', 'surface_solar_irradiance', 'ssi_dtime_from_sst', 'sources_of_ssi',
                           'or_latitude', 'or_longitude', 'or_number_of_pixels', 'sum_square_sst',
                           'adjusted_sea_surface_temperature', 'adjusted_standard_deviation_error',
                           'bias_to_reference_sst', 'standard_deviation_to_reference_sst', 'sources_of_ss'),
             'type': ('byte', 'short', 'float'),
             'name': 'valid_max'},
            {'priority': 'maybe',
             'variables': ('time', 'lat', 'lon', 'sea_surface_temperature', 'analysed_sst', 'sea_ice_fraction',
                           'wind_speed', 'or_latitude', 'or_longitude', 'adjusted_sea_surface_temperature'),
             'type': ('string',),
             'name': 'standard_name'},
            {'priority': 'maybe',
             'variables': ('sea_ice_fraction', 'wind_speed', 'aerosol_dynamic_indicator', 'surface_solar_irradiance'),
             'type': ('string',),
             'name': 'source'},
            {'priority': 'maybe',
             'variables': ('adjusted_sea_surface_temperature',),
             'type': ('string',),
             'name': 'reference'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'positive'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'grid_mapping'},
            {'priority': 'maybe', 'variables': ('none',), 'type': ('string',), 'name': 'coordinates'},
            {'priority': 'maybe',
             'variables': ('quality_level', 'l2p_flags', 'sources_of_wind_speed', 'sources_of_sea_ice_fraction',
                           'sources_of_adi', 'sources_of_ssi'),
             'type': ('string',),
             'name': 'flag_meanings'},
            {'priority': 'maybe',
             'variables': ('quality_level', 'sources_of_wind_speed', 'sources_of_sea_ice_fraction', 'sources_of_adi',
                           'sources_of_ssi'),
             'type': ('byte', 'short'),
             'name': 'flag_values'},
            {'priority': 'maybe', 'variables': ('l2p_flags',), 'type': ('short',), 'name': 'flag_masks'},
            {'priority': 'maybe', 'variables': ('wind_speed',), 'type': ('string',), 'name': 'height'},
        ), (
            {'priority': 'optional', 'variables': ('time', 'lon', 'lat'), 'type': ('string',), 'name': 'axis'},
            {'priority': 'optional',
             'variables': ('sea_surface_temperature', 'adjusted_sea_surface_temperature'),
             'type': ('string',),
             'name': 'depth'},
            {'priority': 'optional',
             'variables': ('sea_ice_fraction', 'wind_speed', 'aerosol_dynamic_indicator', 'surface_solar_irradiance'),
             'type': ('float',),
             'name': 'time_offset'},
        )
    )

    def setup(self, level):
        available_levels = ('L2P', 'L3', 'L4')

        if level is None or level == '':
            level = self.DEFAULT_VERSION
        elif level not in available_levels:
            return abort(400,
                         f'Must specify a GDS2 level in the format "GDS2-parameter:xxx". '
                         f'Available levels are {str(available_levels)}')

        self.version = level

        global_checks = self.add_group('Global Attributes', scope='globals')
        global_checks.add_checker(CheckExistence)
        global_checks.add_checker(CheckTypes)

        global_checks_strings = global_checks.add_group('Required Strings', type='string', priority='required')
        global_checks_strings.add_blueprints([{'name': value} for value in GDS2.REQUIRED_GLOBALS_STRINGS])

        global_checks_floats = global_checks.add_group('Required Floats', type='float', priority='required')
        global_checks_floats.add_blueprints([{'name': value} for value in GDS2.REQUIRED_GLOBALS_FLOATS])

        global_checks_ints = global_checks.add_group('Required Ints', type='int', priority='required')
        global_checks_ints.add_blueprints([{'name': value} for value in GDS2.REQUIRED_GLOBALS_INTS])

        if level == 'L2P':
            l2p = self.add_group('L2P',
                                 description='Geophysical variables derived from Level 1 source data at the same '
                                             'resolution and location as the Level 1 data, typically in a satellite '
                                             'projection with geographic information. These data form the fundamental '
                                             'basis for higher-level GHRSST products and require ancillary data and '
                                             'uncertainty estimates. No adjustments to input SST have been made.')
            l2p.add_checkers(CheckExistence, CheckTypes)

            variables = l2p.add_group('Variables', scope='vars')

            required_variables = variables.add_group('Required')
            required_variables.add_blueprints(GDS2.L2P_variables[0])

            maybe_variables = variables.add_group('Possibly Required')
            maybe_variables.add_blueprints(GDS2.L2P_variables[1])

            varattrs = l2p.add_group('Variable Attributes', scope='varattrs')

            required_varattrs = varattrs.add_group('Required')
            required_varattrs.add_blueprints(GDS2.L2P_varattrs[0])

            maybe_varattrs = varattrs.add_group('Possibly Required')
            maybe_varattrs.add_blueprints(GDS2.L2P_varattrs[1])

            l2p_optional = self.add_group('L2P - Optional', priority='optional',
                                          description='Geophysical variables derived from Level 1 source data at the '
                                                      'same resolution and location as the Level 1 data, typically in '
                                                      'a satellite projection with geographic information. These data '
                                                      'form the fundamental basis for higher-level GHRSST products and '
                                                      'require ancillary data and uncertainty estimates. No '
                                                      'adjustments to input SST have been made.')
            l2p_optional.add_checkers(CheckExistence, CheckTypes)

            optional_variables = l2p_optional.add_group('Variables', scope='vars')
            optional_variables.add_blueprints(GDS2.L2P_variables[2])

            optional_varattrs = l2p_optional.add_group('Variable Attributes', scope='varattrs')
            optional_varattrs.add_blueprints(GDS2.L2P_varattrs[2])

        elif level == 'L3':
            l3 = self.add_group('L3',
                                description='L3 GHRSST products do not use analysis or interpolation procedures to '
                                            'fill gaps where no observations are available')
            l3.add_checkers(CheckExistence, CheckTypes)

            variables = l3.add_group('Variables', scope='vars')

            required_variables = variables.add_group('Required')
            required_variables.add_blueprints(GDS2.L3_variables[0])

            maybe_variables = variables.add_group('Possibly Required')
            maybe_variables.add_blueprints(GDS2.L3_variables[1])

            varattrs = l3.add_group('Variable Attributes', scope='varattrs')

            required_varattrs = varattrs.add_group('Required')
            required_varattrs.add_blueprints(GDS2.L3_varattrs[0])

            maybe_varattrs = varattrs.add_group('Possibly Required')
            maybe_varattrs.add_blueprints(GDS2.L3_varattrs[1])

            l3_optional = self.add_group('L3 - Optional', priority='optional',
                                         description='L3 GHRSST products do not use analysis or interpolation '
                                                     'procedures to fill gaps where no observations are available')
            l3_optional.add_checkers(CheckExistence, CheckTypes)

            optional_variables = l3_optional.add_group('Variables', scope='vars')
            optional_variables.add_blueprints(GDS2.L3_variables[2])

            optional_varattrs = l3_optional.add_group('Variable Attributes', scope='varattrs')
            optional_varattrs.add_blueprints(GDS2.L3_varattrs[2])

        elif level == 'L4':
            l4 = self.add_group('L4',
                                description='Data sets created from the analysis of lower level data that results in '
                                            'gridded, gap- free products. SST data generated from multiple sources of '
                                            'satellite data using optimal interpolation are an example of L4 GHRSST '
                                            'products')
            l4.add_checkers(CheckExistence, CheckTypes)

            variables = l4.add_group('Variables', scope='vars')

            required_variables = variables.add_group('Required')
            required_variables.add_blueprints(GDS2.L4_variables[0])

            varattrs = l4.add_group('Variable Attributes', scope='varattrs')

            required_varattrs = varattrs.add_group('Required')
            required_varattrs.add_blueprints(GDS2.L4_varattrs[0])

            maybe_varattrs = varattrs.add_group('Possibly Required')
            maybe_varattrs.add_blueprints(GDS2.L4_varattrs[1])

            l4_optional = self.add_group('L4 - Optional', priority='optional',
                                         description='Data sets created from the analysis of lower level data that '
                                                     'results in gridded, gap- free products. SST data generated from '
                                                     'multiple sources of satellite data using optimal interpolation '
                                                     'are an example of L4 GHRSST products')
            l4_optional.add_checkers(CheckExistence, CheckTypes)

            optional_variables = l4_optional.add_group('Variables', scope='vars')
            optional_variables.add_blueprints(GDS2.L4_variables[1])

            optional_varattrs = l4_optional.add_group('Variable Attributes', scope='varattrs')
            optional_varattrs.add_blueprints(GDS2.L4_varattrs[2])

        return self
