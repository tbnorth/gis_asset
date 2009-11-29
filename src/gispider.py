try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo import ogr
except ImportError:
    import gdal
    import osr
    import ogr

import os, sys
from pprint import pprint

STARTDIR = "/home/tbrown/Desktop/Proj/GISLab"

class OgrFinder(object):

    EXTENSIONS = [
        '',
        '.shp',  # if it's not a cover it might be a shapefile
        '.dbf',  # if it's not a shapefile it might be a .dbf
    ]

    # text lookup table for GeomType returns
    GeomText = dict([(ogr.__dict__[i], i[3:]) for i in ogr.__dict__
        if i.startswith('wkb')])

    def findOn(self,path):

        datasrc = ogr.OpenShared(path)

        if datasrc and datasrc.GetLayerCount():

            if os.path.isdir(path) and datasrc.GetDriver().GetName() == 'AVCBin':
                    yield {
                        'path':path,
                        'format':'AVCBin',
                        'geomType':ogr.wkbGeometryCollection,
                        'geomText':self.GeomText[ogr.wkbGeometryCollection],

                    }
            else:

                for sublayer in range(datasrc.GetLayerCount()):
                    layer = datasrc.GetLayer(sublayer)
                    for ext in self.EXTENSIONS:
                        path2 = os.path.join(datasrc.GetName(), layer.GetName()+ext)
                        datasrc2 = ogr.OpenShared(path2)
                        if datasrc2:
                            break
                        path2 = os.path.join(datasrc.GetName(), layer.GetName().lower()+ext)
                        datasrc2 = ogr.OpenShared(path2)
                        if datasrc2:
                            break
                    else:
                        print "NO FILE FOR ", layer.GetName()
                    assert  datasrc2.GetLayerCount() == 1
                    yield {
                        'path':path2,
                        'format':datasrc2.GetDriver().GetName(),
                        'geomText':self.GeomText[layer.GetLayerDefn().GetGeomType()],
                        'geomType':layer.GetLayerDefn().GetGeomType(),
                    }
class GdalFinder(object):

    def findOn(self,path):

        datasrc = gdal.OpenShared(path)

        if datasrc:

            yield {
                'path':path,
                'format':datasrc.GetDriver().LongName,
            }

ofinder = OgrFinder()
gfinder = GdalFinder()

for base, dirs, files in os.walk(STARTDIR):

    for dir_ in dirs:
        path = os.path.join(base, dir_)

        skipDir = False
        for l in gfinder.findOn(path):
            pprint(l)
            skipDir = True
        if skipDir:
            dirs.remove(dir_)

        for l in ofinder.findOn(path):
            pprint(l)

    for f in files:
        for l in gfinder.findOn(os.path.join(base,f)):
            pprint(l)

