# Tutorials being followed:
# http://blog.luisrei.com/articles/flaskrest.html
# http://api.mongodb.org/python/current/tutorial.html
# pymongo functions: http://altons.github.io/python/2013/01/21/gentle-introduction-to-mongodb-using-pymongo/

import datetime
import pprint

from bson.json_util import dumps

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)
port_num = int("1234")

from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
                
app.url_map.converters['regex'] = RegexConverter

# Courses
@app.route("/courses/<regex('.*'):param>", methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def go_to_courses(param):
    print "Here is the URI:", param
    if request.method == 'GET':
        return "ECHO: GET\n"

    elif request.method == 'POST':
        return "ECHO: POST\n"

    elif request.method == 'PATCH':
        return "ECHO: PATCH\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"

# Students
@app.route("/students/<regex('.*'):param>", methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def go_to_students(param):
    print "Here is the URI:", param
    if request.method == 'GET':
        req = requests.get(url, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
    elif request.method == 'POST':
        #print request.headers
    #return "ECHO: GET\n"
#request.headers
#werkzeug.wsgi.wrap_file
        return "ECHO: POST students\n"

    elif request.method == 'PATCH':
        return "ECHO: PATCH\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"
        
if __name__ == '__main__':
    app.run(
        debug = True,
        port = port_num
    )