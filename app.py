# use greenlets for greater concurrency
from gevent import monkey; monkey.patch_all()

import bottle
import json
import os
import sys

from bottle import request, response, static_file
from simfile import SMParser
from urlparse import parse_qsl

PROD = '--prod' in sys.argv
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SIMFILES_DIR = PROJECT_ROOT + '/simfiles'

BUILD_DIR = PROJECT_ROOT + '/frontend/build'
STATIC_DIR = BUILD_DIR + '/static'

app = bottle.Bottle()

@app.hook('after_request')
def enable_cors():
    if not PROD:
        response.headers['Access-Control-Allow-Origin'] = '*'

@app.get('/')
def root():
    return static_file('index.html', root=BUILD_DIR)

@app.get('/static/css/<filename>')
def static(filename):
    return static_file(filename, root=STATIC_DIR + '/css')

@app.get('/static/js/<filename>')
def static(filename):
    return static_file(filename, root=STATIC_DIR + '/js')

@app.get('/api/v1/simfiles')
def api_v1_simfiles():
    return json.dumps([{'value': sim, 'label': sim}
                       for sim in os.listdir(SIMFILES_DIR)])

@app.get('/api/v1/simfiles/<name>', method='GET')
def api_v1_simfiles_name(name):
    query_params = dict(parse_qsl(request.query_string))

    # strip invalid params
    [query_params.pop(param) for param in query_params.keys()
     if not param in SMParser.analyze.func_code.co_varnames]

    try:
        return {
            "result": SMParser(open(SIMFILES_DIR + '/' + os.path.basename(name)).read()).analyze(**query_params)
        }
    except Exception as e:
        return { "errors": "Could not load simfile (bad param?): " + e.message }

def run():
  bottle.debug(not PROD)
  bottle.run(
    app=app, 
    host='0.0.0.0',
    port=os.environ['PORT'],
    reloader=not PROD
  )

if __name__=='__main__':
  run()

