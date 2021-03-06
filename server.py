#! /usr/bin/env python

###############################################################################
#                       Add 3d Libraries to python path.                      #
###############################################################################

import os
import sys

AE_PATH = "/usr/local/google_appengine"
APP_PATH = os.path.abspath(".")
EXTRA_PATHS = [
    APP_PATH, AE_PATH,
    os.path.join(AE_PATH, 'lib', 'jinja2-2.6'),
    os.path.join(AE_PATH, 'lib', 'webapp2-2.5.2'),
    os.path.join(AE_PATH, 'lib', 'webob-1.2.3')
]
sys.path = EXTRA_PATHS + sys.path

###############################################################################
#                             Web request handlers.                           #
###############################################################################

import jinja2
import webapp2
import ee
import config
import json

BIOMASS_DATA_ID = "users/shengwu/biomass/1126"

class MainHandler(webapp2.RequestHandler):
    def get(self, path=''):
        mapId = GetBiomassMapId()
        template_values = {
            'eeMapId': mapId['mapid'],
            'eeToken': mapId['token']
        }
        template = JINJA2_ENVIRONMENT.get_template('index.html')
        self.response.out.write(template.render(template_values))     

class PixelValueHandler(webapp2.RequestHandler):
    def get(self):
        lat = self.request.get('lat')
        lng = self.request.get('lng')
        pnt = ee.Geometry.Point(float(lng), float(lat))
        img = ee.Image(BIOMASS_DATA_ID)
        val = {}
        val['biomass'] = img.reduceRegion(ee.Reducer.mean(), pnt).getInfo()['b1']
        val['longitude'] = lng
        val['latitude']  = lat
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(val))

class RegionValueHandler(webapp2.RequestHandler):
    def get(self):
        coords = self.request.get('coordinates')
        plg = ee.Geometry.Polygon([float(x) for x in coords.split(",")])
        img = ee.Image(BIOMASS_DATA_ID)
        #reducer = ee.Reducer.count().combine(ee.Reducer.mean()) #.combine(ee.Reducer.minMax())
        val = {}
        count = img.reduceRegion(ee.Reducer.count(), plg)
        mean  = img.reduceRegion(ee.Reducer.mean(), plg)
        minmax= img.reduceRegion(ee.Reducer.minMax(), plg)
        total = img.reduceRegion(ee.Reducer.sum(), plg)
        stddev= img.reduceRegion(ee.Reducer.stdDev(), plg)
        val["count"] = count.getInfo()['b1']
        val["area"]  = plg.area().getInfo()
        val["sum"]   = total.getInfo()['b1']
        val["mean"]  = mean.getInfo()['b1']
        val["max"]   = minmax.getInfo()['b1_max']
        val["min"]   = minmax.getInfo()['b1_min']
        val["stddev"]= stddev.getInfo()['b1']
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(val))

class TestHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA2_ENVIRONMENT.get_template('test.html')
        template_values = {}
        self.response.out.write(template.render(template_values))        

app = webapp2.WSGIApplication([
    ('/pixelVal', PixelValueHandler),
    ('/regionVal', RegionValueHandler),
    ('/test.html', TestHandler),
    ('/', MainHandler)
])

###############################################################################
#                               Helpers.                                      #
###############################################################################

def GetBiomassMapId():
    img = ee.Image(BIOMASS_DATA_ID)
    return img.getMapId({
        'min': 0.0,
        'max': 250.0,
        'palette': '000000,00FF00'
    })

###############################################################################
#                             Initialization.                                 #
###############################################################################

JINJA2_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

EE_CREDENTIALS = ee.ServiceAccountCredentials(
    config.EE_ACCOUNT, config.EE_PRIVATE_KEY_FILE
)

ee.Initialize(EE_CREDENTIALS)

