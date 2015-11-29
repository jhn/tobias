#### Python 2.7 
#import pdb
import httplib, urllib, base64, json
import os,http
import sys
body = {"URL": "http://www.burgermedia.nl/media/k2/items/cache/9911ecbea07a30e7c89fdadbe8a058e8_XL.jpg" } 
print body
print (open('1.jpg', "rb").read())[:50]

#sys.exit()

headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '-------------------------------------------------------------------------------------------',
} 

params = urllib.urlencode({
    # Request parameters
    'analyzesFaceLandmarks': 'false',
    'analyzesAge': 'true',
    'analyzesGender': 'true',
    'analyzesHeadPose': 'false',
})

try:
    conn = httplib.HTTPSConnection('api.projectoxford.ai')
    conn.request("POST", "/face/v0/detections?%s" % params, open('1.jpg', "rb").read(), headers) #json.dumps(body) #open('1.jpg', "rb").read()
    response = conn.getresponse()
    data = response.read()
    print data
    #jdata = json.loads(data)
    #for each in jdata:
    #    print each['attributes']
    conn.close()
except Exception as e:
    print("Errno")