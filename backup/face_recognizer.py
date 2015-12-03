#!/usr/bin/python

# ------------------- Start of imports/preliminaries -------------------

webcamOrURL = 0 # 0 uses webcam, 1 uses URL

# Import the required modules
import pdb
import cv2, os # Facial recognition and motion detection! Google Voice Account Integration
import numpy as np
import urllib # For downloading images from URL
from numpy import genfromtxt
from PIL import Image
from cv2 import *
import pyttsx # Speech synthesis
import speech_recognition as sr # Google speech recognition
import winsound
import time
from random import randint
import shutil
import smtplib # Emailing with attachments!
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

import httplib, base64, json
import http
import sys
#import pyopencv as cv

# For face detection we will use the Haar Cascade provided by OpenCV.
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

# For face recognition we will the the LBPH Face Recognizer 
recognizer = cv2.createLBPHFaceRecognizer()

# ------------------- End of imports/preliminaries -------------------
# >>>>>>>>>>>>>>>>>>>>>>>> Start of Functions >>>>>>>>>>>>>>>>>>>>>>>>

def captureAndAnalyze():
    cam = cv2.VideoCapture(0)
    for x in range(0, 5):
        img = cam.read()[1]
        cv2.imwrite('1.png',img)

    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '557adf6d8efe48d792526481f3b41125'
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
        
        cv2.imwrite('1.png',img)
        
        conn.request("POST", "/face/v0/detections?%s" % params, open('1.png', "rb").read(), headers)
        response = conn.getresponse()
        data = response.read()
        jdata = json.loads(data)
        conn.close()
        return jdata
    except Exception as e:
        print "Errno"
        return 0


        
def getImageFromURLorWebcam():
    if webcamOrURL == 0:
        cam = cv2.VideoCapture(0)
        for x in range(0, 10):
            img = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
            cv2.imwrite('1.png',img)
    return img
    
# detects motion over a specified threshold
def motionDetection():
    while True:
        try:
            t_minus = getImageFromURLorWebcam()
        except:
            t_minus = getImageFromURLorWebcam()
        try:
            t = getImageFromURLorWebcam()
        except:
            t = getImageFromURLorWebcam()
            
        dst = 0
        sum = 0
        err = 0

        dst = cv2.absdiff(t_minus, t)
        dst = dst.sum()
        print dst
        if dst > 500000:
            return 1
            
def displayAdForJdata(jdata):
    print jdata
    if jdata == []:
        print "blank RET ZERO still"
        return 0
    for each in jdata:
        gender = each['attributes']['gender']
        age = each['attributes']['age']
        print gender, age
    if gender == 'male' and age > 50:
        img = cv2.imread('me.jpg', CV_LOAD_IMAGE_COLOR)
    if gender == 'female' and age > 50:
        img = cv2.imread('fe.jpg', CV_LOAD_IMAGE_COLOR)
    if gender == 'male' and age <= 50 and age > 35:
        img = cv2.imread('ma.jpg', CV_LOAD_IMAGE_COLOR)
    if gender == 'female' and age <= 50 and age > 35:
        img = cv2.imread('fa.jpg', CV_LOAD_IMAGE_COLOR)
    if gender == 'male' and age <= 35:
        img = cv2.imread('ms.png', CV_LOAD_IMAGE_COLOR)
    if gender == 'female' and age <= 35:
        img = cv2.imread('fs.png', CV_LOAD_IMAGE_COLOR)
        
    cv2.destroyAllWindows()
    #cv2.namedWindow("test", cv2.WND_PROP_FULLSCREEN)          
    #cv2.setWindowProperty("test", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
    cv2.imshow('Advertisement', img)
    cv2.waitKey(10000)
            
            
def faceDetection():
    print "getting img"
    getImageFromURLorWebcam()
    print "got img"
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    img = cv2.imread('1.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        print "FACES DETECTED"
        return 1
    return 0

# >>>>>>>>>>>>>>>>>>>>>>>> End of Functions >>>>>>>>>>>>>>>>>>>>>>>>
# @@@@@@@@@@@@@@@@@@@@@@@ Start of Execution @@@@@@@@@@@@@@@@@@@@@@@

while True:
    while True:
        if faceDetection() == 1:
            break
            
    print "NOW FACE REC stuff"
            
    jdata = captureAndAnalyze()
    displayAdForJdata(jdata)
    
    
