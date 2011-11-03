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

class OgrFinder(object):

    EXTENSIONS = [
        '',
        '.shp',  # if it's not a cover it might be a shapefile
        '.dbf',  # if it's not a shapefile it might be a .dbf
    ]

    # text lookup table for GeomType returns
    # {1: 'Point', 2: 'LineString', ...}
    GeomText = dict([(ogr.__dict__[i], i[3:]) for i in ogr.__dict__
        if i.startswith('wkb')])
    TypeText = dict([(ogr.__dict__[i], i[3:]) for i in ogr.__dict__
        if i.startswith('OFT')])

    @staticmethod
    def get_table_info(path):
        dataset = ogr.Open(path)
        layer = dataset.GetLayer(0)
        d = {
            'records': layer.GetFeatureCount(),
            'attrib': [],
        }
        schema = layer.GetLayerDefn()
        for i in range(0, schema.GetFieldCount()):
            fld = schema.GetFieldDefn(i)
            d['attrib'].append({
                'name': fld.GetNameRef(),
                'type': OgrFinder.TypeText.get(fld.GetType(), None),
            })
        return d

    def findOn(self, path):
        
        if path.lower().endswith('.shx'):
            return

        datasrc = ogr.OpenShared(path)

        if datasrc and datasrc.GetLayerCount():

            if os.path.isdir(path) and datasrc.GetDriver().GetName() == 'AVCBin':
                    yield {
                        'path':path,
                        'format':'AVCBin',
                        'geomType':ogr.wkbGeometryCollection,
                        'geomText':self.GeomText[ogr.wkbGeometryCollection]
                    }
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

                    yield {
                        'path':path,
                        'layer':sublayer.GetName(),
                        'format':datasrc.GetDriver().GetName(),
                        'geomText':self.GeomText[sublayer.GetLayerDefn().GetGeomType()],
                        'geomType':sublayer.GetLayerDefn().GetGeomType(),
                    }
class GdalFinder(object):

    def __init__(self):
        self.devnull = open('/dev/null','w')

    def findOn(self, path):

        stderr = sys.stderr
        sys.stderr = self.devnull
        datasrc = gdal.OpenShared(path)
        sys.stderr = stderr

        if datasrc:

            yield {
                'path':path,
                'format':datasrc.GetDriver().LongName,
            }

def search_path(startdir, use_gdal=True, use_ogr=True,
    use_dir=True, use_file=True, extensions=[]):
    
    if use_gdal:
        gfinder = GdalFinder()
    if use_ogr:
        ofinder = OgrFinder()
    
    for base, dirs, files in os.walk(startdir, topdown=True):
    
        culls = set()
        
        if use_dir:
            for dir_ in dirs:
                
                path = os.path.join(base, dir_)
        
                if use_gdal:
                    for l in gfinder.findOn(path):
                        d = dict(l)
                        d['find_type'] ='GDAL dir'
                        yield d
                        culls.add(dir_)
        
                if use_ogr:
                    for l in ofinder.findOn(path):
                        d = dict(l)
                        d['find_type'] ='OGR dir'
                        yield d

        for cull in culls:
            dirs.remove(cull)
    
        if use_file:
            
            for f in files:
                
                if (extensions and
                    os.path.splitext(f)[1].lower() not in extensions):
                    continue
                
                if use_gdal:
                    for l in gfinder.findOn(os.path.join(base,f)):
                        d = dict(l)
                        d['find_type'] ='GDAL file'
                        yield d
                        
                if use_ogr:
                    for l in ofinder.findOn(os.path.join(base,f)):
                        d = dict(l)
                        d['find_type'] ='OGR file'
                        yield d

if __name__ == '__main__':
    
    import sys
    
    STARTDIR = "/home/tbrown/Desktop/Proj/GISLab"
    STARTDIR = sys.argv[1]
    
    for i in search_path(STARTDIR, use_gdal=False, use_dir=False):
        if not i['path'].lower().endswith('.dbf'):
            continue
        pprint(i)
        pprint(OgrFinder.get_table_info(i['path']))
