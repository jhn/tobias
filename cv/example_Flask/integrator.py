# The integrator micro-service
# It logs every transaction but will not always inform the other MS about the changes

# *: do not tell other MS about this (the change will not affect them)
# It is essential that each MS, including partitions, has its own distinct port

import os
import sys
import datetime
import pprint
import thread

from bson.json_util import dumps
import requests

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)

#python integrator.py <courseMS_URL> <courseMS_port> <number of student partitions> (for each student partition, 
#		list the following:) <studentMS_URL> <studentMS_port>
#ex. python integrator.py http://localhost:9001 9001 1 http://localhost:9002 9002

courses = None
coursesPort = None
students = {} # dictionary of studentsURL: studentsPort
acceptedOps = ['POST', 'GET', 'PUT', 'DELETE']

def main(argv):
	if (len(argv) < 5):
		print "Too few command-line arguments."
		sys.exit(1)

	ports = []
	expectedUniquePorts = 0

	global courses
	courses = argv[0]

	global coursesPort
	coursesPort = argv[1]

	# Check to make sure coursesPort is an integer and a valid port
	if (not isinstance(int(coursesPort), int) or int(coursesPort) < 1024): 
		print "argv[1] must be a valid port"
		sys.exit(1)

	ports.append(coursesPort)
	expectedUniquePorts += 1

	numberOfPartitions = int(argv[2])
	argNumber = 3

	global students
	for i in range(numberOfPartitions):
		if (not isinstance(int(argv[argNumber+1]), int) or int(argv[argNumber+1]) < 1024):
			print "argv[" + str(argNumber+1) + "] must be a valid port"
			sys.exit(1)
		students[argv[argNumber]] = argv[argNumber+1]
		ports.append(argv[argNumber+1])
		argNumber += 2
		expectedUniquePorts += 1

	# ensure that the ports are all distinct!
	if (len(set(ports)) < expectedUniquePorts):
		print "Each port number must be distinct (including partitions)."
		sys.exit(1)
	app.run()

# Check that the requester's port belongs to courses or one of the students micro-services
def checkPort(port):
	if (int(port) == int(coursesPort)):
		return True
	for k, v in students.iteritems():
		if int(port) == int(v):
			return True
	return False	

# Creates response to return to the user
def response(data, code):
	js = json.dumps(data)
	resp = Response(js, status = code, mimetype='application/json')
	return resp

# Log message format: <timestamp> <requester IP> [<pkeys>] [<fkeys>] [<original non-primary key>] [<changed non-primary key>] <CRUD operation>
# Leave any given array as empty parentheses if there aren't any
def writeToLog(message):
	with open("log.txt", "a") as myfile:
		myfile.write(message + "\n")

def deleteFromLog(timestamp):
	# Read all the lines
	f = open("log.txt", "r")
	lines = f.readlines()
	f.close()

	# Look for the line to delete
	lineNumber = 1
	for l in lines:
		if timestamp in l:
			break
		lineNumber += 1

	# Write all lines except for the one to delete into a new file
	lineCount = 1
	message = ""
	n = open("newlog.txt", "a")
	for line in lines:
		if lineCount != lineNumber:
			n.write(line)
		else:
			message += line
		lineCount += 1
	n.close()
	if (len(message) > 0):
		os.rename("newlog.txt", "log.txt")
	return message

# Method to help split the key and prepare it in the correct format for the log
def formatKey(key):
	substring = " ["
	key = key.replace("_", " ")
	for i in range(len(key)):
		substring += key[i]
	substring += "]"
	return substring

# Call the other micro-services
def notifyMS(requesterPort, message):
	print "Port: " + requesterPort
	print "Course: " + coursesPort
	sender = None
	# determine if students or courses was the sender
	if (int(requesterPort) == int(coursesPort)):
		sender = 'course'
	else:
		for k, v in students.iteritems():
			if int(requesterPort) == int(v):
				sender = 'student'

	# determine who to send request to based on the sender
	if (sender == 'course'): # broadcast to students
		for k, v in students.iteritems():
			print "CONTACTED STUDENTS"
			data = {'important change':message}
			#r = requests.post(k, data = json.dumps(data))
	else:
		print "CONTACTED COURSES"
		data = {'important change':message}
		#r = requests.post(courses, data = json.dumps(data))

# POST with primary key only (primary keys are cid or uid)
# The integrator will inform the other MS about these changes
@app.route('/integrator/<primary_key>', methods = ['POST'])
def post_key_POST_OR_DEL(primary_key):
	data = json.loads(request.data) #convert data into dictionary
	requester_port = data["port"]
	if (requester_port is None):
		data = {'error': 'No port specified'}
		return response(data, 400)

	# figure out who the sender was
	sender = None
	if (int(requester_port) == int(coursesPort)):
		sender = 'course'
	else:
		for k, v in students.iteritems():
			if int(requester_port) == int(v):
				sender = 'student'
	print data
	for k, v in data.iteritems():
		print "key: " + str(k)
		print "value: " + str(v)

	# figure out the sender's action

	data = {'received':request.data}
	return response(data, 200)
"""
for k,v in request.form.iteritems():
        if k == "uid":
            return "You can't update a student's UID", 409
    v1 = find_user(uid)
    for k,v in request.form.iteritems():
        posts.update({"uid":uid},{"$set":{k:v}})
    data = json.dumps({"port": port_num, "v1" : v1, "v2": find_user(uid), "cid": None})
    post_event(uid, data, PUT)
    return "Updates made successfully", 200
			sender = 'student'
"""

if __name__ == '__main__':
	main(sys.argv[1:])