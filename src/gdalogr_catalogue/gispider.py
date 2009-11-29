try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo import ogr
except ImportError:
    import gdal
    import osr
    import ogr

import os, sys

STARTDIR = "/home/tbrown/Desktop/Proj/GISLab"

EXTENSIONS = []#'', '.shp', '.dbf']
sdf f
class OgrScan(object):
    def __init__(self, x):
        self.dat = ogr.OpenShared(x)
        self.ok = self.dat
    def childCount(self):
        return self.dat.GetLayerCount()
    def getName(self):
        return self.dat.GetName()
    def getDriver(self):
        return self.dat.GetDriver()
    def getChild(self, i):
        return self.dat.GetLayer(i)
class GdalScan(object):
    def __init__(self, x):
        self.dat = gdal.OpenShared(x)
        self.ok = self.dat
    def childCount(self):
        return self.dat.GetLayerCount()
    def getName(self):
        return self.dat.GetName()
    def getDriver(self):
        return self.dat.GetDriver()
    def getChild(self, i):
        return self.dat.GetLayer(i)


for path, dirs, files in os.walk(STARTDIR):

    o = OgrScan(path)

    if o and o.childCount():
        print o.getName()
        print o.getDriver().GetName()
        print o.childCount(), ' '.join([o.getChild(i).GetName()
          for i in range(o.childCount())])
        print

        for sl in range(o.childCount()):
            ly = o.getChild(sl)
            for ext in EXTENSIONS:
                l = OgrScan(os.path.join(o.getName(), ly.getName()+ext))
                if l.ok:
                    break
                l = OgrScan(os.path.join(o.getName(), ly.getName().lower()+ext))
                if l.ok:
                    break

            else:
                print "NO ", ly.getName()
            print ' ', l.getName()
            print ' ', l.getDriver().GetName()
            print ' ', l.childCount(), ' '.join([l.getChild(i).GetName()
              for i in range(l.childCount())])
            print

