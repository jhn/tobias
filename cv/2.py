# -*- coding: utf-8 -*-
    
from flask import Flask
from flask import Response
from flask import stream_with_context
from flask import request

from werkzeug.routing import BaseConverter

import requests
import json
import pickle

import httplib, urllib, base64
import http
import sys
import difflib

import os
with open('api.keys') as f:
    keys = f.readlines()

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
                
app.url_map.converters['regex'] = RegexConverter

headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '-----------------------------------------------------------------------------------------------------------',
}

params = urllib.urlencode({
    # Request parameters
    'analyzesFaceLandmarks': 'false',
    'analyzesAge': 'true',
    'analyzesGender': 'true',
    'analyzesHeadPose': 'false',
})

#Any URIs coming in with "/courses..." are re-routed in this function
@app.route("/recognize", methods = ['GET', 'POST'])
def route():
    data = {}
    #A POST request is incoming
    if request.method == 'POST':
        #print request.get_data()
        #print len(request.get_data().splitlines())
        #print ("\n".join(request.get_data().splitlines()[4:-1]))[-50:]
        #print (open('1.jpg', "rb").read())[-50:]
        #print ("\n".join(request.get_data().splitlines()[4:-1]))[:50]
        #print (open('1.jpg', "rb").read())[:50]
        #print len()
        #print len(open('1.jpg', "rb").read())
        #WORKED? "\n".join(request.get_data().splitlines()[4:-1])
        
        '''
        a = "\n".join(request.get_data().splitlines()[4:-1])
        b = open('1.jpg', "rb").read()
        print a == b
        print len(a)
        print len(b)
        import re
        a = "\n".join(request.get_data().splitlines()[4:-1])
        c = re.split(r'[\n]+', request.get_data())
        c = "\n".join(c[4:-1])
        for i in xrange(120):
            if c[i:i+1] != b[i:i+1]:
                print i
                break
        print i
        if c[103] != b[103]:
            print "NOT EQUAL AT 103"
        print "b:" + b[103] + "-"
        if c[103] == "\t":
            print "tab"
        if b[103] == "\n":
            print "newl"
        print "c:" + c[103] + "-"
        c=c.replace(c[103],"")
        print c == b
        print len(c)
        print len(b)
        print "done"
        '''
        
        
        
        
        
        #print a == b
        #print len(a)
        #print len(b)
        #array = [i for i in xrange(len(a)) if c[i] != b[i]]
        #print array
        #import unicodedata
        #from string import whitespace
        #for each in array:
        #    print repr(b[each]), each
            #for c in whitespace:
            #    if b[each] == c:
            #        print c
            #        print "sdafkljhasldkjhsldf"
                
            #print "a\r"+(b[each])+"\rb"
        #decoded = base64.b64decode(request.get_data())
        #data = json.loads(decoded)
        #print decoded
        #print len("\n".join(request.get_data().splitlines()[4:-1]))
        #print len("\n".join(request.get_data().splitlines()[4:-1]).decode('utf-8'))
        #print Differ().compare("".join(request.get_data().splitlines()[4:-1]), open('1.jpg', "rb").read())
        return "computer"
        try:
            conn = httplib.HTTPSConnection('api.projectoxford.ai')
            conn.request("POST", "/face/v0/detections?%s" % params, c, headers) # request.get_data().splitlines()[4:] # open('1.jpg', "rb").read()
            response = conn.getresponse()
            data = response.read()
            jdata = json.loads(data)
            for each in jdata:
                print each['attributes']
            return json.dumps(map((lambda x: x['attributes']), jdata))
            conn.close()
        except Exception as e:
            print("Error")
    return "Online"
        
if __name__ == '__main__':
    app.run(
        debug = True,
        port = 1234
    )