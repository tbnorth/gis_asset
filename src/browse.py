"""CherryPy app which browses a file system"""
#import sys; sys.path.append('..')

import os, os.path
from scgj_lib.template import Template, afilter
template = Template(os.path.join(os.path.dirname(__file__), 'tmpl'))

import cherrypy

#from models import Session, User, Class
#import models
#from scgj_lib.drender import DRender, DRid

#DRender(User)
#DRender(Class)

#from sqlalchemy.orm import eagerload, clear_mappers

from genshi import HTML
from genshi.core import Markup

import glob
class Index:
    def __init__(self):
        self.counter = 0
        self.basedir = '/'
    @cherrypy.expose
    @template.output('index2.html')
    def index(self):
        first = HTML(self.dirent())
        return dict(first='/', jscripts=["browse.js"])
    @cherrypy.expose
    @template.output('dirent.html')
    def direntold(self):
        entries = [{'name':'one'}, {'name':'two'}, {'name':'three'}]
        entries[2]['name'] = str(self.counter)
        self.counter += 1
        return template.render(entries = entries)
    @cherrypy.expose
    @template.output('dirent.html')
    def dirent(self, *args):
        path = '/'+'/'.join(args)+'/*'
        entries = [{'name': os.path.basename(i),
                    'type': 'd' if os.path.isdir(i) else 'f'
                    } for i in glob.glob(path)]
        return dict(entries = entries)
def main():
    cherrypy.quickstart(Index(), '/', config='browse.conf')

if __name__=='__main__':main()
