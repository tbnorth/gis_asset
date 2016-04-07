# GIS asset indexer

Two parts, a spider that searches local file systems for GIS and tabular
(.csv, .xls, .mdb, etc.) data an indexes it, and a web interface that
allows searching by attribute names, row counts, geometry types, etc.

See also:  https://github.com/tbnorth/gis_asset_app
Django app that serves the collected data

Current status (201604):

 - old code being revamped
 - this repo. contains an old CherryPy interface, deprecated in
   favor of the Django version https://github.com/tbnorth/gis_asset_app
