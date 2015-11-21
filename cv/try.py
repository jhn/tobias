#### Python 2.7 
import pdb
import httplib, urllib, base64, json
body = {"URL": "http://www.burgermedia.nl/media/k2/items/cache/9911ecbea07a30e7c89fdadbe8a058e8_XL.jpg" } 

headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '6e87c925b14b487fb7d38cd1eb4358c7',
} 

params = urllib.urlencode({
    # Request parameters
    'analyzesFaceLandmarks': 'false',
    'analyzesAge': 'true',
    'analyzesGender': 'true',
    'analyzesHeadPose': 'false',
})

#params = 'faceRectangles'

try:
    conn = httplib.HTTPSConnection('api.projectoxford.ai')
    conn.request("POST", "/face/v0/detections?%s" % params, json.dumps(body) , headers)
    response = conn.getresponse()
    data = response.read()
    #print(data)
    jdata = json.loads(data)
    for each in jdata:
        print each['attributes']
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
    
    