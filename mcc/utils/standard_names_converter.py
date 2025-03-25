#!/usr/bin/env python

"""
===========================
standard_names_converter.py
===========================

Generate standard name JSON based on an xml file.

"""

from collections import defaultdict
from json import dump
from sys import argv

from bs4 import BeautifulSoup

TABLE_FN = 'cf-standard-name-table-26.xml'


def parse_aliases(alias_generator):
    aliases = defaultdict(list)

    for alias in alias_generator:
        alias_name = alias.get('id')
        real_name = alias.entry_id.text
        aliases[real_name].append(alias_name)

    return aliases


def parse_entries(soup):
    aliases = parse_aliases(soup.findAll('alias'))

    for entry in soup.findAll('entry'):
        name = entry.get('id')

        # `or` statements lets us set '' -> None
        yield name, {
            'aliases': aliases.get(name, None),
            'description': entry.description.text or None,
            'canonical_units': entry.canonical_units.text or None,
            'amip': entry.amip.text or None,
            'grib': entry.grib.text or None,
        }


def main(fn):
    # BE VERY VAREFUL WITH THE PARSER
    # 'xml' will truncate files and mess everything up
    soup = BeautifulSoup(open(fn).read(), 'lxml')
    data = {standard_name: data for standard_name, data in parse_entries(soup)}

    j = {
        'title': 'CF Standard Names Table',
        'version': soup.find('version_number').text,
        'last_modified': soup.find('last_modified').text,
        'data': data,
        'count': len(data),
    }

    fn = j['title'].split(' ')
    fn.append(j['version'])

    with open('-'.join(fn) + '.json', 'w') as f:
        dump(j, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    if len(argv) > 1:
        main(argv[1])
    else:
        main(TABLE_FN)
