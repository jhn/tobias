# -*- coding: utf-8 -*-
    
from flask import Flask
from flask import Response
from flask import stream_with_context
from flask import request

from werkzeug.routing import BaseConverter

import requests
import json
import pickle

import os
with open('api.keys') as f:
    keys = f.readlines()

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
                
app.url_map.converters['regex'] = RegexConverter

#Any URIs coming in with "/courses..." are re-routed in this function
@app.route("/recognize", methods = ['GET', 'POST'])
def route():
    data = {}
 #   for k,v in request.form.iteritems():
 #       print "here"
 #       if k == "file":
 #           print k
    #A POST request is incoming
    if request.method == 'POST':
        #file = request.form['file']
        #imagefile = request.files.get('file', '')

        json_resp = requests.post( 'http://api.sightcorp.com/api/detect/',
              data   = { 'app_key'   : keys[0][:-1],
                         'client_id' : keys[1] },
              files  = { 'img'       : request.files.get('file', '') } ) #request.get_data()
        print "Response : ", json_resp.text

        return json_resp.text
    return "Online"
        
if __name__ == '__main__':
    app.run(
        debug = True,
        port = 1234
    )