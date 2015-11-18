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

# Import and initialize MongoDB
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client.test_database
collection = db.test_collection
posts = db.posts # DO NOT DELETE THIS LINE!!!
collection.remove({}) # start clear
posts.remove() # start clear

# Globals
port_num = int("9002")
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# Prepopulate DB when students.py is restarted by stat if on debug mode
post = {"first_name": "Agustin",
        "last_name": "Chanfreau",
        "uid": "ac3680",
        "email": "ac3680@columbia.edu",
        "cid_list": ["COMS123", "COMS1234", "COMS12345"],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Mel",
        "last_name": "Chaasdau",
        "uid": "ab3680",
        "email": "ab3680@columbia.edu",
        "cid_list": ["COMS123", "COMS1234", "COMS12345"],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]}
post_id = posts.insert_one(post).inserted_id

# GET .../students - returns all information for all students
@app.route('/students', methods = [GET])
def all_users():
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    return dumps(l)

# GET .../students/<uid> - returns all information for specified student
@app.route('/students/<uid>', methods = [GET])
def find_user(uid):
    record = get_record(uid)
    if record:
        print "Found matching record for UID: ", uid
        return dumps(record)
    else:
        return not_found()

# GET .../students/<uid>/courses - returns enrolled courses for specified student
@app.route('/students/<uid>/courses', methods = [GET])
def get_student_courses(uid):
    record = get_record(uid)
    if record:
        print "Found matching record for UID: ", uid
        return dumps(record["cid_list"])
    else:
        return not_found()

# POST .../students - Create a new student
# TODO: return appropriate error when uid is not provided (currently 400 which indicates server error)
@app.route('/students', methods = [POST])
def create_new_student():
    print "Called create_new_student"
    print request.form
    uid = request.form['uid']
    print "uid: " + uid
    if get_record(uid):
        return "Resource already exists\n", 409
    # Initialize courses list as empty list
    posts.insert({"uid":uid})
    for k,v in request.form.iteritems():
        if k == "uid":
            continue
        elif k == "cid_list":
            # Add each course in a comma-delimited string to cid_list
            for cid in v.split(','):
                posts.update({"uid":uid},{"$push":{"cid_list": cid}})
        else:
            posts.update({"uid":uid},{"$set":{k:v}})
    print posts
    data = json.dumps({"port": port_num, "v1" : "", "v2": find_user(uid), "cid": "", "verb": POST})
    post_event(uid, data, POST)
    message = "New student(" + uid + ") created\n"
    return message, 201

# PUT .../students/<uid> - Update student field
@app.route('/students/<uid>', methods=[PUT])
def update_student(uid):
    print "now we are updating the following uid: ", uid
    for k,v in request.form.iteritems():
        if k == "uid":
            return "You can't update a student's UID", 409
    v1 = find_user(uid)
    for k,v in request.form.iteritems():
        if k == "cid_list":
            continue
        elif k == "cid_list":
            for cid in v.split(','):
                posts.update({"uid":uid},{"$push":{"cid_list": cid}})
        else:
            posts.update({"uid":uid},{"$set":{k:v}})
    data = json.dumps({"port": port_num, "v1" : v1, "v2": find_user(uid), "cid": "", "verb": PUT})
    post_event(uid, data, PUT)
    return "Updates made successfully", 200

#Add one course to student.
@app.route('/students/<uid>/courses', methods=[POST])
def add_course(uid):
    cid = request.form['cid']
    record = get_record(uid)
    if record:
        if check_course(uid, cid):
            message = "Course(" + cid + ") already exists\n"
            return message, 409
        v1 = find_user(uid)
        posts.update({"uid":uid},{"$push":{"cid_list": cid}})
        message = "Added course(" + cid + ") to student(" + uid + ")\n"
        data = json.dumps({"port": port_num, "v1" : v1, "v2": find_user(uid), "cid": cid, "verb": POST})
        post_event(uid, data, POST)
        return message, 200
    else:
        return not_found()

# Remove one course from student.
@app.route('/students/<uid>/courses/<cid>', methods=[DELETE])
def remove_course(uid, cid):
    record = get_record(uid)
    if record:
        if not check_course(uid, cid):
            message = "Course(" + cid + ") does not exist\n"
            return message, 409
        v1 = find_user(uid)
        posts.update({"uid":uid},{"$pull":{"cid_list": cid}})
        message = "Removed course(" + cid + ") from student(" + uid + ")\n"
        data = json.dumps({"port": port_num, "v1" : v1, "v2": find_user(uid), "cid": cid, "verb": DELETE})
        post_event(uid, data, DELETE)
        return message, 200
    else:
        return not_found()

# DELETE .../students/<uid> - Delete a student
@app.route('/students/<uid>', methods=[DELETE])
def delete_student(uid):
    record = get_record(uid)
    if record:
        v1 = find_user(uid)
        posts.remove({"uid":uid})
        data = json.dumps({"port": port_num, "v1" : v1, "v2": "", "cid": "", "verb": DELETE})
        post_event(uid, data, DELETE)
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

# Post student change event (non-GET requests) to integrator
def post_event(uid, user_data, action):
    url = 'http://127.0.0.1:5000/integrator/' + uid
    print "POST to integrator: " + url
    res = requests.post(url, data=user_data) # data=json.dumps(find_user(uid))
    print 'response from server:', res.text

# Returns a record given a UID (uni)
def get_record(uid):
    record = posts.find_one({"uid": uid})
    if record:
        return record
    else:
        return 0

# Finds a course in a record given a UID (student identifier) and a CID (course identifier)
def check_course(uid, cid):
    record = posts.find_one({"uid": uid, "cid_list": cid})
    print record
    if record:
        return record
    else:
        return 0

if __name__ == '__main__':
    app.run(
        debug = True,
        port = port_num
    )
