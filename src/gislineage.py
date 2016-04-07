"""
gislineage.py - Give a listing of GIS files in a directory to
aid lineage reconstruction.

Terry Brown, Wed Jan  9 13:22:23 2013
"""

import os
import sys
import time

import gispider

def main():

    paths = {}

    for asset in gispider.search_path(sys.argv[1]):
        # print asset['path']
        paths[asset['path']] = asset

    for asset in paths.itervalues():
        stat = os.stat(asset['path'])
        asset['mtime'] = stat.st_mtime
        asset['ctime'] = stat.st_ctime

    assets = sorted(paths.values(), key=lambda x: x['mtime'])

    common_path_depth = 0
    while all([i['path'].split('/')[common_path_depth] ==
               assets[0]['path'].split('/')[common_path_depth]
               for i in assets]):
        common_path_depth += 1

    for asset in assets:
        path = asset['path'].split('/')[common_path_depth+1:]
        path = '/'.join(path)
        print time.asctime(time.localtime(asset['mtime'])), path

if __name__ == '__main__':
    main()
