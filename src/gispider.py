try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo import ogr
except ImportError:
    import gdal
    import osr
    import ogr

import os, sys, glob, json
from pprint import pprint

import time

OPEN_TIME = {}


def os_walk(path, topdown=None):
    """Implement os.walk to avoid UnicodeDecode errors,
    or at least trap them.

    Assumes top down, parameter just for compatibility.
    """

    dirs = []
    files = []

    for i in glob.glob(os.path.join(path, '*')):

        if os.path.isdir(i):
            dirs.append(os.path.basename(i))
        elif os.path.isfile(i):
            files.append(os.path.basename(i))

    yield path, dirs, files

    for d in dirs:

        try:
            for i in os_walk(os.path.join(path, d)):
                yield i
        except UnicodeDecodeError:
            print("BAD DIRECTORY %r / %r" % (path, d))


class OgrFinder(object):

    EXTENSIONS = [
        '',
        '.shp',  # if it's not a cover it might be a shapefile
        '.dbf',  # if it's not a shapefile it might be a .dbf
    ]

    # text lookup table for GeomType returns
    # {1: 'Point', 2: 'LineString', ...}
    GeomText = dict(
        [(ogr.__dict__[i], i[3:]) for i in ogr.__dict__ if i.startswith('wkb')]
    )
    TypeText = dict(
        [(ogr.__dict__[i], i[3:]) for i in ogr.__dict__ if i.startswith('OFT')]
    )

    @staticmethod
    def get_table_info(path, layer=None):
        dataset = ogr.Open(path)
        if not dataset:
            return {}
        if layer:
            layer = dataset.GetLayer(layer)
        else:
            layer = dataset.GetLayer(0)
        d = {
            'records': layer.GetFeatureCount(),
            'attrib': [],
        }
        schema = layer.GetLayerDefn()
        for i in range(0, schema.GetFieldCount()):
            fld = schema.GetFieldDefn(i)
            d['attrib'].append(
                {
                    'name': fld.GetNameRef(),
                    'type': OgrFinder.TypeText.get(fld.GetType(), None),
                }
            )
        return d

    def findOn(self, path):

        if path.lower().endswith('.shx'):
            return

        OPEN_TIME['OGR ' + path] = time.time()

        datasrc = ogr.OpenShared(path)

        OPEN_TIME['OGR ' + path] = time.time() - OPEN_TIME['OGR ' + path]

        if datasrc and datasrc.GetLayerCount():

            if (
                os.path.isdir(path)
                and datasrc.GetDriver().GetName() == 'AVCBin'
            ):
                try:
                    ascii_path = path.encode('ascii')
                    yield {
                        'path': path,
                        'format': 'AVCBin',
                        'geomType': ogr.wkbGeometryCollection,
                        'geomText': self.GeomText[ogr.wkbGeometryCollection],
                    }
                except UnicodeDecodeError:
                    pass
            else:

                for sublayer_n in range(datasrc.GetLayerCount()):
                    sublayer = datasrc.GetLayer(sublayer_n)
                    # for ext in self.EXTENSIONS:
                    #     path2 = os.path.join(datasrc.GetName(), layer.GetName()+ext)
                    #     datasrc2 = ogr.OpenShared(path2)
                    #     if datasrc2:
                    #         break
                    #     path2 = os.path.join(datasrc.GetName(), layer.GetName().lower()+ext)
                    #     datasrc2 = ogr.OpenShared(path2)
                    #     if datasrc2:
                    #         break
                    # else:
                    #     print "NO FILE FOR", layer.GetName()
                    # assert datasrc2.GetLayerCount() == 1

                    # yield {
                    #     'path':path2,
                    #     'format':datasrc2.GetDriver().GetName(),
                    #     'geomText':self.GeomText[layer.GetLayerDefn().GetGeomType()],
                    #     'geomType':layer.GetLayerDefn().GetGeomType(),
                    # }

                    try:
                        ascii_path = path.encode('ascii')
                        yield {
                            'path': path,
                            'name': sublayer.GetName(),
                            'layer': sublayer.GetName(),
                            'format': datasrc.GetDriver().GetName(),
                            'geomText': self.GeomText[
                                sublayer.GetLayerDefn().GetGeomType()
                            ],
                            'geomType': sublayer.GetLayerDefn().GetGeomType(),
                        }
                    except UnicodeDecodeError:
                        pass


class GdalFinder(object):

    # text lookup table for Type returns
    # {1: 'Point', 2: 'LineString', ...}

    RATTypeText = dict(
        [
            (gdal.__dict__[i], i[4:])
            for i in gdal.__dict__
            if i.startswith('GFT_')
        ]
    )

    def __init__(self):
        try:
            self.devnull = open('/dev/null', 'w')
        except IOError:
            self.devnull = open('nul:', 'w')

    @staticmethod
    def get_table_info(path, layer=None):
        dataset = gdal.OpenShared(path)
        if dataset:
            if layer:
                layer = dataset.GetRasterBand(layer)
            else:
                layer = dataset.GetRasterBand(1)
            table = layer.GetDefaultRAT()
        else:
            table = None
        if not table:
            return {'records': 0, 'attrib': []}

        d = {
            'records': table.GetRowCount(),
            'attrib': [],
        }
        # schema = layer.GetLayerDefn()
        for i in range(0, table.GetColumnCount()):
            # fld = schema.GetFieldDefn(i)
            d['attrib'].append(
                {
                    'name': table.GetNameOfCol(i),
                    'type': GdalFinder.RATTypeText.get(
                        table.GetTypeOfCol(i), None
                    ),
                }
            )
        return d

    def findOn(self, path):

        OPEN_TIME['GDAL ' + path] = time.time()

        stderr = sys.stderr
        sys.stderr = self.devnull
        datasrc = gdal.OpenShared(path)
        sys.stderr = stderr

        OPEN_TIME['GDAL ' + path] = time.time() - OPEN_TIME['GDAL ' + path]

        if datasrc:

            transform = datasrc.GetGeoTransform()
            cellsx, cellsy = datasrc.RasterXSize, datasrc.RasterYSize
            bands = datasrc.RasterCount

            geom_type = (
                datasrc.GetRasterBand(1) and datasrc.GetRasterBand(1).DataType
            )

            yield {
                'name': os.path.basename(path),
                'path': path,
                'format': datasrc.GetDriver().LongName,
                'minx': transform[0],
                'maxx': transform[0] + cellsx * transform[1],
                'miny': transform[3] + cellsy * transform[5],
                'maxy': transform[3],
                'cellsx': cellsx,
                'cellsy': cellsy,
                'sizex': transform[1],
                'sizey': transform[5],
                'geomText': gdal.GetDataTypeName(geom_type),
                'geomType': geom_type,
                'srid': -1,  # FIXME
            }


def search_path(
    startdir,
    use_gdal_on=('file', 'dir'),
    gdal_extensions=[],
    gdal_exclude=['.aux', '.ovr'],
    use_ogr_on=('file',),
    ogr_extensions=['.dbf', '.kml', '.gpx',],
    ogr_exclude=[],
):

    # FIXME: refactor as prioritized list of finders
    if use_gdal_on:
        gfinder = GdalFinder()
    if use_ogr_on:
        ofinder = OgrFinder()
    use_dir = 'dir' in use_gdal_on or 'dir' in use_ogr_on
    use_file = 'file' in use_gdal_on or 'file' in use_ogr_on

    for base, dirs, files in os_walk(startdir, topdown=True):

        # print "%s: %d dirs, %d files" % (base, len(dirs), len(files))

        culls = set()  # don't descend dirs recognized as data sources

        if use_dir:
            for dir_ in dirs:

                path = os.path.join(base, dir_)

                if 'dir' in use_gdal_on:
                    for l in gfinder.findOn(path):
                        d = dict(l)
                        d['find_type'] = 'GDAL dir'
                        yield d
                        culls.add(dir_)

                if 'dir' in use_ogr_on:
                    for l in ofinder.findOn(path):
                        d = dict(l)
                        d['find_type'] = 'OGR dir'
                        yield d
                        culls.add(dir_)

        for cull in culls:
            dirs.remove(cull)

        if use_file:

            for f in files:

                ext = os.path.splitext(f)[1].lower()

                path = os.path.join(base, f)

                if (
                    'file' in use_gdal_on
                    and ext not in gdal_exclude
                    and (not gdal_extensions or ext in gdal_extensions)
                ):

                    for l in gfinder.findOn(path):
                        d = dict(l)
                        d['find_type'] = 'GDAL file'
                        yield d

                if (
                    'file' in use_ogr_on
                    and ext not in ogr_exclude
                    and (not ogr_extensions or ext in ogr_extensions)
                ):

                    for l in ofinder.findOn(path):
                        d = dict(l)
                        d['find_type'] = 'OGR file'
                        yield d

def add_table_info(items):
    for i in items:
        if 'OGR' in i['find_type']:
            OPEN_TIME['OGR TABLE ' + i['path']] = time.time()
            table_info = OgrFinder.get_table_info(i['path'], i.get('layer'))
            OPEN_TIME['OGR TABLE ' + i['path']] = (
                time.time() - OPEN_TIME['OGR TABLE ' + i['path']]
            )
        else:
            OPEN_TIME['GDAL TABLE ' + i['path']] = time.time()
            table_info = GdalFinder.get_table_info(i['path'], i.get('layer'))
            OPEN_TIME['GDAL TABLE ' + i['path']] = (
                time.time() - OPEN_TIME['GDAL TABLE ' + i['path']]
            )

        i['table_info'] = table_info

        yield i

def default_search(startdir):
    for i in search_path(
        startdir,
        use_gdal_on=('dir', 'file'),  # 'dir',
        use_ogr_on=('file',),  # 'file',
        ogr_extensions=[
            '.csv',
            '.dbf',
            '.shp',
            '.kml',
            '.gpx',
            '.xls',
            '.xlsx',
            '.mdb',
        ],
    ):
        yield i


def main():
    import sys

    startdir = sys.argv[1]

    print("[")

    for n, i in enumerate(add_table_info(default_search(startdir))):

        if n > 0:
            print(',')
        print(json.dumps(i))
        if n > 100:
            pass
            # break

        sys.stderr.write("%s %s\n" % (n, i['path']))

        top = sorted([(v, k) for k, v in OPEN_TIME.items()], reverse=True)
        # pprint(top[:5])

    print("]")


if __name__ == '__main__':
    main()
