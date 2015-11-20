# -*- coding: utf-8 -*-
    
from flask import Flask
from flask import Response
from flask import stream_with_context
from flask import request

from werkzeug.routing import BaseConverter

import requests
import json
import pickle

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
    #A POST request is incoming
    if request.method == 'POST':
        json_resp = requests.post( 'http://api.sightcorp.com/api/detect/',
              data   = { 'app_key'   : '0cf15ecbf14444f1a74c86be27e7a63e',
                         'client_id' : '31939259487b4ce59c07b54b6ffd733d' },
              files  = { 'img'       : request.get_data() } )
        print "Response : ", json_resp.text

        return json_resp.text
    return "0"
        
if __name__ == '__main__':
    app.run(
        debug = True,
        port = 1234
    )