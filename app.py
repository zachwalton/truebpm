# use greenlets for greater concurrency
from gevent import monkey; monkey.patch_all()

import bottle
import json
import os

from bottle import request, response, static_file
from simfile import SMParser
from urlparse import parse_qsl

PROD = True
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
def static_css(filename):
    return static_file(filename, root=STATIC_DIR + '/css')

@app.get('/static/js/<filename>')
def static_js(filename):
    return static_file(filename, root=STATIC_DIR + '/js')

@app.get('/api/v1/simfiles')
def api_v1_simfiles():
    sims = sorted(os.listdir(SIMFILES_DIR), key=lambda s: s.lower())
    return json.dumps([{'value': sim, 'label': sim}
                       for sim in sims])

@app.get('/api/v1/simfiles/<name>', method='GET')
def api_v1_simfiles_name(name):
    query_params = dict(parse_qsl(request.query_string))

    # strip invalid params
    [query_params.pop(param) for param in query_params.keys()
     if not param in SMParser.analyze.func_code.co_varnames]

    try:
        with open(SIMFILES_DIR + '/' + os.path.basename(name)) as fh:
            parsed = SMParser(fh.read())
            # just override this for now, not all charts have a Hard/Expert chart
            query_params['difficulty'] = parsed.charts['Single'].keys()[-1]
            return {
                "result": parsed.analyze(**query_params)
            }
    except Exception as e:
        return { "errors": "Could not load simfile (bad param?): " + e.message }

def run():
  bottle.debug(not PROD)
  bottle.run(
    app=app, 
    host='0.0.0.0',
    port=os.environ.get('PORT', 8000),
    reloader=not PROD,
    server='gunicorn',
    workers=8,
  )

if __name__=='__main__':
  run()

