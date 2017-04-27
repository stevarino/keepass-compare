#!/usr/bin/env python
'''Keepass Compare

Compares two keepass database files. Supports KeePassX and KeePass2 files (v3 and v4).

https://github.com/stevarino/keepass-compare
'''

import argparse
from collections import namedtuple
import getpass
import itertools
import libkeepass

Node = namedtuple("Node", ['ref', 'path', 'uuid', 'strings', 'parent_id'])
Change = namedtuple("Change", ['type', 'path', 'details'])

def main(file1, file2, password1=None, password2=None, **kwargs):
    """Compares two keepass files given the associated passwords."""

    items1 = scan_kdb(file1, password1, kwargs['compare'])
    items2 = scan_kdb(file2, password2, kwargs['compare'])

    keys1 = set(items1.keys())
    keys2 = set(items2.keys())
    changes = []

    # deletions
    for key in keys1.difference(keys2):
        changes.append(Change('-', items1[key].path, ['Removed']))
    # additions
    for key in keys2.difference(keys1):
        changes.append(Change('+', items2[key].path, ['Added']))
    # modifications
    for key in keys1.intersection(keys2):
        details = compare_item(items1[key], items2[key])
        if details:
            changes.append(Change('!', items2[key].path, details))

    changes.sort(key=lambda c: c.path)

    print('')
    if not changes:
        print("No changes found.")
    for change in changes:
        print("{}{}".format(change.type, change.path))
        for detail in change.details:
            print("    {}".format(detail))

def scan_kdb(file, password, compare):
    '''Returns a dict with all Groups/Entries in a KDB file.'''
    paths = {'/KeePassFile/Root': ['']}
    items = {}


    with libkeepass.open(file, password=password) as kdb:
        for item in itertools.chain(kdb.obj_root.findall('.//Group'),
                                    kdb.obj_root.findall('.//Group/Entry')):
            parent = item.getroottree().getpath(item.getparent())
            strings = find_item_strings(item)

            if item.tag == 'Group':
                name = item.find('./Name').text
            elif item.tag == 'Entry':
                name = strings['Title']
            path = paths[parent]+[name]

            paths[item.getroottree().getpath(item)] = path

            path_display = '/'.join(path)
            if item.tag == 'Group':
                path_display += '/'

            key = path
            if compare == 'uuid':
                key = item.find('./UUID').text
                parent_id = ''
                if len(paths[parent]) > 1:
                    parent_id = item.getparent().find('./UUID').text
            elif compare == 'path':
                key = tuple(path)
                parent_id = '/'.join(paths[parent]) + '/'
            else:
                raise NotImplementedError("Unrecognized compare method")

            items[key] = Node(item, path_display, item.find('./UUID').text,
                              strings, parent_id)

    return items

def find_item_strings(item):
    '''Returns a dictionary of strings found in the item.'''
    strings = {}
    for string in item.findall('./String'):
        strings[string.find('./Key').text] = string.find('./Value').text
    return strings

def compare_item(rec1, rec2):
    '''Compares two records, attempting to find any properties that have changed.'''
    details = []

    if rec1.parent_id != rec2.parent_id:
        details.append("Changed parents.")

    fields = {'Group': ['Name', 'IconID', 'Notes'],
              'Entry': ['IconID', 'ForegroundColor', 'ForegroundColor', 'OverrideURL',
                        'Tags']}

    for field in fields[rec1.ref.tag]:
        if rec1.ref.find("./"+field).text != rec2.ref.find("./"+field).text:
            details.append("{} field changed.".format(field))

    strings1 = set(rec1.strings.keys())
    strings2 = set(rec2.strings.keys())

    for string in strings1.difference(strings2):
        details.append("{} string removed.".format(string))
    for string in strings2.difference(strings1):
        details.append("{} string added.".format(string))
    for string in strings2.intersection(strings1):
        if rec1.strings[string] != rec2.strings[string]:
            details.append("{} string modified.".format(string))

    return details

def parse_args():
    """Parses sys.args and returns a dictionary."""
    parser = argparse.ArgumentParser("Performs a diff analysis against two " +
                                     "KeePass files. If a password is not " +
                                     "specified it will be read through " +
                                     "stdin.")
    parser.add_argument("file1", help="The first, or original file")
    parser.add_argument("file2", help="The second, or modified file")
    parser.add_argument("-p", "--password",
                        help="The password for both files")
    parser.add_argument("-p1", "--password1",
                        help="The password for the first file")
    parser.add_argument("-p2", "--password2",
                        help="The password for the second file")
    parser.add_argument("--compare", choices=['uuid', 'path'], default='uuid',
                        help="Compare the entries by UUID (default) or path")

    args = vars(parser.parse_args())

    if args['password'] is not None:
        args['password1'] = args['password']
        args['password2'] = args['password']
    if args['password1'] is None:
        print('Passsword for file "{}"'.format(args['file1']))
        args['password1'] = getpass.getpass()
    if args['password2'] is None:
        print(('Passsword for file "{}" (press enter to reuse the first ' +
               'password)').format(args['file2']))
        args['password2'] = getpass.getpass()
        if not args['password2']:
            args['password2'] = args['password1']

    return args



if __name__ == '__main__':
    main(**parse_args())
