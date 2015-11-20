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

#returns a list of ports, or a list with only a "0" if the student's first letter is not a letter
def getPort(param):
    with open('config.txt', 'rb') as handle:
        routingTable = pickle.loads(handle.read())
    UIDisThere = False
    portList = []
    if param == "":
        for key, value in routingTable.items():
            if value in portList:
                a=1
            else:
                portList.append(value)
        return portList
    for key, value in routingTable.items():
        try:
            if key == param[1]:
                portList.append(value)
                UIDisThere = True
                break
        except:
            portList = []
            portList.append(0)
            return portList
    if UIDisThere == False:
        portList.append(0)
        return portList
    return portList
    
#Returns port as variable - not as list
def postPort(param):
    with open('config.txt', 'rb') as handle:
        routingTable = pickle.loads(handle.read())
    UIDisThere = False
    for key, value in routingTable.items():
        if key == param[0]:
            SinglePort = value
            UIDisThere = True
            break
    if UIDisThere == False:
        SinglePort = 0
        return SinglePort
    return SinglePort


# For courses
@app.route("/courses<regex('.*'):param>", methods = ['GET', 'POST', 'PUT', 'DELETE'])
def coursesRoute(param):
    data = {}
    if request.method == 'GET':
        #ifparam[1]
        req = requests.get("http://127.0.0.1:9002/students" + param, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
    elif request.method == 'POST':
        print "the magic letter is:", request.form['firstName'][0]
        data = {"firstName": request.form['firstName'],
        "lastName": request.form['lastName'],
        "uid": request.form['uid'],
        "email": request.form['email'],
        "enrolledCourses": request.form['enrolledCourses'],
        "pastCourses": request.form['pastCourses']}
        req = requests.post("http://127.0.0.1:9002/students" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
    elif request.method == 'PUT':
        for k,v in request.form.iteritems():
            print k,v
            data.update({k:v})
        req = requests.put("http://127.0.0.1:9002/students" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
    elif request.method == 'DELETE':
        req = requests.delete("http://127.0.0.1:9002/students" + param, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

        
        
@app.route("/students<regex('.*'):param>", methods = ['GET', 'POST', 'PUT', 'DELETE'])
def studentsRoute(param):
    portList = getPort(param)
    print portList
    if portList[0] == 0: # UID starts with a letter
        return "Invalid UID", 400
    data = {}
    if request.method == 'GET':
        if len(portList) == 1:
            req = requests.get("http://127.0.0.1:" + str(portList[0]) + "/students" + param, stream = True)
            return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
        if len(portList) == 3:
            req1 = requests.get("http://127.0.0.1:" + str(portList[0]) + "/students" + param, stream = True)
            req2 = requests.get("http://127.0.0.1:" + str(portList[1]) + "/students" + param, stream = True)
            req3 = requests.get("http://127.0.0.1:" + str(portList[2]) + "/students" + param, stream = True)
            return req1.text + req2.text + req3.text # SEE IF WAY TO DO THIS BETTER
    elif request.method == 'POST':
        for k,v in request.form.iteritems():
            print k,v
            data.update({k:v})
        print request.form['uid']
        
        singlePort = postPort(request.form['uid'])
        if singlePort == 0: # UID !start with a letter
            return "Invalid UID", 400
            
        print "--------PORT AFTER IS", singlePort
        req = requests.post("http://127.0.0.1:" + str(singlePort) + "/students" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
    elif request.method == 'PUT':
        for k,v in request.form.iteritems():
            print k,v
            data.update({k:v})
        req = requests.put("http://127.0.0.1:" + str(portList[0]) + "/students" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
    elif request.method == 'DELETE':
        req = requests.delete("http://127.0.0.1:" + str(portList[0]) + "/students" + param, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

if __name__ == '__main__':
    app.run(
        debug = True,
        port = 1235
    )