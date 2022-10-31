import subprocess
 
# This is a sample Python/Flask app showing Domino's App publishing functionality.
# You can publish an app by clicking on "Publish" and selecting "App" in your
# quick-start project.

import os
import json
import flask
from flask import request, redirect, url_for, jsonify
import numpy as np
 
class ReverseProxied(object):
  def __init__(self, app):
      self.app = app
  def __call__(self, environ, start_response):
      script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
      if script_name:
          environ['SCRIPT_NAME'] = script_name
          path_info = environ['PATH_INFO']
          if path_info.startswith(script_name):
              environ['PATH_INFO'] = path_info[len(script_name):]
      # Setting wsgi.url_scheme from Headers set by proxy before app
      scheme = environ.get('HTTP_X_SCHEME', 'https')
      if scheme:
        environ['wsgi.url_scheme'] = scheme
      # Setting HTTP_HOST from Headers set by proxy before app
      remote_host = environ.get('HTTP_X_FORWARDED_HOST', '')
      remote_port = environ.get('HTTP_X_FORWARDED_PORT', '')
      if remote_host and remote_port:
          environ['HTTP_HOST'] = f'{remote_host}:{remote_port}'
      return self.app(environ, start_response)
 
app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)


# ----------------------------------------------------------------
# INIT
# ----------------------------------------------------------------

# LOAD THE FORM JSON SCHEMA
with open('forms/titles.schema.json', 'r') as f:
  jsonschema = json.load(f)

# init the list of displays
with open('forms/titles-databook_Displays.json', 'r') as f:
  displays = json.load(f)

# ----------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------

# Homepage 
# ----------------------------------------------------------------
@app.route('/')
def index_page():
  return flask.render_template("index.html", jsonschema=json.dumps(jsonschema), displays=displays)

# Display TFLID
# ----------------------------------------------------------------
@app.route('/display/<string:tflid>', methods=['GET'])
def display(tflid):
  # first off, get the display for this TFLID (or False if not exist)
  this_display = next((d for d in displays if d["tflid"]==tflid), False)
  schemavalue = jsonschema             # get the original (empty) form schema..
  schemavalue['value'] = this_display  # ..and add this display to it
  # render the page with the schema pre-loaded with the TFLID diaplsy values
  return flask.render_template("index.html", jsonschema=json.dumps(schemavalue), tflid=tflid, displays=displays)


# Submit changes to current display
# ----------------------------------------------------------------
@app.route('/submit', methods = ['POST'])
def submit():
  # find the index if the posted tflid
  tflid = request.form['tflid']
  idx = next((i for i, d in enumerate(displays) if d['tflid']==tflid),-1)
  # if it already exists in the display list then just update it
  if idx >= 0:
    # update the in-memory displays with this display
    displays[idx] = request.form.to_dict()
  else:
    # This is a NEW DISPLAY ID so append it to list of displays
    displays.append(request.form.to_dict())
  # write displays to file (if possible)
  METADATA_DIR = os.getenv('DOMINO_ARTIFACTS_DIR') + '/results'
  if os.path.isdir(METADATA_DIR):
    with open(METADATA_DIR+'/titles.json', 'w') as f: 
      f.write(json.dumps(displays, indent=4))
  return redirect(url_for('display', tflid=tflid))