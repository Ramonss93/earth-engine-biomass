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
        img = ee.Image("users/shengwu/AGB")
        val = img.reduceRegion(ee.Reducer.mean(), pnt)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(val.getInfo()))
        

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/pixelVal', PixelValueHandler)
])

###############################################################################
#                               Helpers.                                      #
###############################################################################

def GetBiomassMapId():
    img = ee.Image("users/shengwu/AGB")
    return img.getMapId({
        'min': 0.0,
        'max': 215.0,
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

