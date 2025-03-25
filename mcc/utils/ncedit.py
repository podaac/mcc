#!/usr/bin/env python

"""
=========
ncedit.py
=========

Quick and dirty script for use in adding, editing, and deleting
globals attrs and varattrs in an existing netCDF file.
Does not save types other than unicode strings.

"""

from os.path import abspath
from sys import argv, exit

from netCDF4 import Dataset


def print_dimensions(ds):
    print('        Dimension         | Value')

    for dim_name, dim_obj in ds.dimensions.items():
        n = str(len(dim_obj))
        dim_size = n if not dim_obj.isunlimited() else 'UNLIMITED (currently {0})'.format(n)
        line = '{:25s} | {:20s}'.format(dim_name, dim_size)
        print(line)

    print('-' * 80)


def prompt_set_varattrs(ds):
    varattrs = {
        variable: ds.variables.get(variable)
        for variable in ds.variables
    }

    for var_name, var_obj in varattrs.items():
        print('Variable: {0}'.format(var_name))

        for attr_name, attr_value in vars(var_obj).items():
            print('\t {a} = "{v}"'.format(a=attr_name, v=attr_value))

    print('for attributes of variables only')
    print('add, edit, delete [a/e/d]?')

    s = input('> ')

    if s == 'a':
        print('name of variable?')
        n = input('> ')
        print('attribute name?')
        a = input('> ')
        print('value of {n}:{a}?'.format(n=n, a=a))
        v = input('> ')
        # TODO: only saves strings
        setattr(ds.variables[n], a, v)
    elif s == 'd':
        print('name of variable?')
        n = input('> ')
        print('name of attribute? [choices: {s}]'.format(s=', '.join(list(vars(ds.variables[n]).keys()))))
        a = input('> ')
        delattr(ds.variables[n], a)
    else:
        print('name of variable?')
        n = input('> ')
        print('name of attribute? [choices: {s}]'.format(s=', '.join(list(vars(ds.variables[n]).keys()))))
        a = input('> ')
        print('new value of {n}:{a}?'.format(n=n, a=a))
        v = input('> ')
        # TODO: only saves strings
        setattr(ds.variables[n], a, v)


def prompt_set_global(ds):
    global_attributes = ds.__dict__

    # TODO: add type
    print(' # |   Global Attribute   | Value ')

    for i, key in enumerate(global_attributes):
        value = global_attributes[key]
        line = '{:2d} | {:20s} | {:60s}'.format(i, key, value)
        print(line)

    print('add, edit, delete [a/e/d]?')

    s = input('> ')

    if s == 'a':
        print('name of global?')
        a = input('> ')
        print('value of {a}?'.format(a=a))
        v = input('> ')
        # TODO: only saves strings
        setattr(ds, a, v)
    elif s == 'd':
        print('name of global?')
        n = input('> ')
        delattr(ds, n)
    else:
        print('name of global?')
        a = input('> ')
        print('new value of {a} (current value {v})?'.format(a=a, v=getattr(ds, a)))
        n = input('> ')
        setattr(ds, a, n)


def main(fn, type):
    with Dataset(fn, 'a') as ds:
        print_dimensions(ds)

        if type == '-v':
            prompt_set_varattrs(ds)
        else:
            prompt_set_global(ds)


if __name__ == '__main__':
    if len(argv) != 3:
        print('./ncedit [-g|-v] <netcdf file>')
        exit(1)

    main(abspath(argv[2]), argv[1])
