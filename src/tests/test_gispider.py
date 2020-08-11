"""
test_gispider.py - tests for gispider.py

Terry N. Brown Brown.TerryN@epa.gov Mon 08/10/2020
"""
import json
import os

import pytest

import gispider

FORMATS = [
    'CSV',
    'GPX',
    'Arc/Info Binary Grid',
    'KML',
    'GeoTIFF',
    'ESRI Shapefile',
]


@pytest.fixture(scope='module')
def gold():
    """Static list of expected entries."""
    return json.load(
        open(os.path.join(os.path.dirname(__file__), "test_data.json"))
    )


@pytest.fixture(scope='module')
def current():
    """List of entries returned by current code."""
    return list(gispider.add_table_info(gispider.default_search('test_data')))


def format_test(gold, current, format=None):
    """Check for expected entries for a format"""
    entries = [i for i in gold if i['format'] == format]
    assert entries
    for entry in entries:
        assert entry in current, (format, entry['path'])


# generate separate tests for separate formats
for format in FORMATS:
    globals()[
        f'test_{format}'
    ] = lambda gold, current, format=format: format_test(
        gold, current, format=format
    )
