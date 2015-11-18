import datetime
import pprint
import requests

from bson.json_util import dumps

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)

# Import and initialize Mongo DB
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client.test_database
collection = db.test_collection
posts = db.posts
collection.remove({}) # start clear
posts.remove() # start clear

# Globals
port_num = int("9005")
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# POST (WILL BE REMOVED LATER
# Pre-populates DB when students.py is restarted by stat if on debug mode
post = {"firstName": "Agustin",
        "lastName": "Chanfreau",
        "uid": "ac3680",
        "email": "ac3680@columbia.edu",
        "enrolledCourses": ["COMS123", "COMS1234", "COMS12345"],
        "pastCourses": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"firstName": "Mel",
        "lastName": "Chaasdau",
        "uid": "ab3680",
        "email": "ab3680@columbia.edu",
        "enrolledCourses": ["COMS123", "COMS1234", "COMS12345"],
        "pastCourses": ["COMS948", "COMS94", "COMS9841"]}
post_id = posts.insert_one(post).inserted_id

# Returns a record given a UID (uni)
def getRecordForUID(uid):
    record = posts.find_one({"uid": uid})
    if record:
        return record
    else:
        return 0

# GET .../students - returns all information for all students
@app.route('/students', methods = [GET])
def all_users():
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    return dumps(l)

# GET .../students/<uid> - returns all information for specified student
@app.route('/students/<uid>', methods = [GET])
def api_users(uid):
    record = getRecordForUID(uid)
    if record:
        print "Found matching record for UID: ", uid
        #postEvent(uid, GET)
        return dumps(record)
    else:
        return not_found()

# GET .../students/<uid>/courses - returns enrolledCourses for specified student
@app.route('/students/<uid>/courses', methods = [GET])
def get_student_courses(uid):
    record = getRecordForUID(uid)
    if record:
        print "Found matching record for UID: ", uid
        #postEvent(uid, GET)
        return dumps(record["enrolledCourses"])
    else:
        return not_found()

# POST .../students - Create a new student
@app.route('/students', methods=[POST])
def createNewStudent():
    print type(request.data)
    print type(request.data)
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    uid = request.form['uid']
    if getRecordForUID(uid):
        return "Resource already exists", 409
    email = request.form['email']
    enrolledCourses = request.form['enrolledCourses']
    pastCourses = request.form['pastCourses']
    print firstName, lastName, uid, email, enrolledCourses, pastCourses
    post = {"firstName": firstName,
            "lastName": lastName,
            "uid": uid,
            "email": email,
            "enrolledCourses": enrolledCourses,
            "pastCourses": pastCourses}
    print post
    post_id = posts.insert_one(post).inserted_id
    #postEvent(uid, POST) 
    return "New Student Created", 201

# PUT .../students/<uid> - Update student field
@app.route('/students/<uid>', methods=[PUT])
def updateStudent(uid):
    print "now we are updating the following uid: ", uid
    for k,v in request.form.iteritems():
        if k == "uid":
            return "You can't update a student's UID", 409
    for k,v in request.form.iteritems():
        posts.update({"uid":uid},{"$set":{k:v}})
    #postEvent(uid, PUT)
    return "Updates made successfully", 200

# DELETE .../students/<uid> - Delete a student
@app.route('/students/<uid>', methods=[DELETE])
def deleteStudent(uid):
    record = getRecordForUID(uid)
    if record:
        posts.remove({"uid":uid})
        #postEvent(uid, DELETE)
        return "Student deleted successfully", 200
    else:
        return "Not Found", 404

# Handle nonexistent routes
@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

# Post student change event to integrator
def postEvent(uid, method):
    res = requests.post('http://127.0.0.1:5000/integrator/' + str(port_num) + '/' + uid + '/' + method)
    print 'response from server:', res.text

if __name__ == '__main__':
    app.run(
        debug = True,
        port = port_num
    )
