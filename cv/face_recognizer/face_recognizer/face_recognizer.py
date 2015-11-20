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
import cleverbot # API Chatting with a bot that came close to passing the Turing Test in 2011
cb1 = cleverbot.Cleverbot()

# Initialize speech recognition and learn to ignore ambient noise by listening for 1 second
engine = pyttsx.init()
r = sr.Recognizer()
with sr.Microphone() as source:
    audio = r.adjust_for_ambient_noise(source)

rate = engine.getProperty('rate')
engine.setProperty('rate', rate-60) # By default the voice speaks too fast, this slows down the WPM spoken

# For face detection we will use the Haar Cascade provided by OpenCV.
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

# For face recognition we will the the LBPH Face Recognizer 
recognizer = cv2.createLBPHFaceRecognizer()

# Run server asynchronously to communicate with ROS section programs
import subprocess
import sys
subprocess.Popen("mongoose.exe")

#Initialize the communication file to 1 (no action is taken by ROS part of program)
fo = open("Web\\communication", "wb")
fo.write("0");
fo.close()

#Configure our Gmail and Google Voice account with these settings
gmail_user = "asampr2@gmail.com"
gmail_pwd = "MIMEBase"

# ------------------- End of imports/preliminaries -------------------
# >>>>>>>>>>>>>>>>>>>>>>>> Start of Functions >>>>>>>>>>>>>>>>>>>>>>>>

def getImageFromURLorWebcam():
    time.sleep(0.5)
    if webcamOrURL == 0:
        cam = cv2.VideoCapture(0)
        for x in range(0, 5):
            img = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
        namedWindow("cam-test",CV_WINDOW_AUTOSIZE)
        imshow("cam-test",img)
        cv2.waitKey(1000)
        destroyAllWindows()
    else:
        urllib.urlretrieve("http://160.39.143.190:8080/snapshot?topic=/wide_stereo/left/image_color", "0001.jpg")
        namedWindow("cam-test",CV_WINDOW_AUTOSIZE)
        img = cv2.imread('0001.jpg',0)
        imshow("cam-test",img)
        cv2.waitKey(1000)
        os.remove('0001.jpg')
        destroyAllWindows()
    return img
    
def mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

#Works with motion detection function below to compare three images
def diffImg(t0, t1, t2):
    d1 = cv2.absdiff(t2, t1)
    d2 = cv2.absdiff(t1, t0)
    return cv2.bitwise_and(d1, d2)
    
# detects motion over a specified threshold
def motionDetection():
    #cam = cv2.VideoCapture(0)  
    try:
        # Read three images first:
        t_minus = getImageFromURLorWebcam()
        t = getImageFromURLorWebcam()
        t_plus = getImageFromURLorWebcam()
    except:
        print "fail"
    dst = 0
    sum = 0
    err = 0
    while True:
        dst = cv2.absdiff(t_minus, t)
        dst = dst.sum()

        if dst > 500000:
            return 1
            # Read next image
            t_minus = t
            t = t_plus
            t_plus = getImageFromURLorWebcam()            
            
# Have a conversation with the robot using CleverBot
def chat():
    engine.say("What would you like to talk about?")
    engine.runAndWait()
    while True:
        winsound.Beep(500,200)
        with sr.Microphone() as source:
            audio = r.listen(source)
        winsound.Beep(400,200)
        try:
            word = r.recognize(audio)
            if word == "I gotta go":
                engine.say("Talk to you later!")
                engine.say("Have a great day!")
                engine.runAndWait()
                return 0
            engine.say(cb1.ask(word)) # This sends whatever the person said into CleverBot API as text, then speaks the returned text
            engine.runAndWait()
        except: # we did not understand the spoken audio
            engine.say("What?")
            engine.runAndWait()
            continue
    return 0
        
# Listen for a 'yes' or a 'no' or an instruction to chat (phrase must contain 'chat' or 'talk', for example 'can we talk?')
# This function does not enforce that a 'yes' or 'no' is said, and will quit if there is any error
def listenYNTimeout():
    winsound.Beep(500,200)
    with sr.Microphone() as source:
        audio = r.listen(source)
    winsound.Beep(400,200)
    try:
        word = r.recognize(audio)
        print word
        if 'yes' in word:
            print "it is"
            return 1
        if 'No' in word:
            return 0
        if 'chat' in word:
            chat()
        if 'talk' in word:
            chat()
    except LookupError:
        return 0

# Listen for a 'yes' or a 'no' or an instruction to chat (phrase must contain 'chat' or 'talk', for example 'can we talk?') in a loop
# until one of the three is spoken by the user
def listenYN():
    while True: # Run until it recognizes either Yes or No
        winsound.Beep(500,200)
        with sr.Microphone() as source:
            audio = r.listen(source)
        winsound.Beep(400,200)
        
        try:
            word = r.recognize(audio)
            if 'yes' in word:
                print "You said yes!!!"
                return 1
            if 'No' in word:
                print "You said no!!!"
                return 0
        except LookupError:
            engine.say('I didnt catch that')
            engine.runAndWait()

def getEmail(subjectID): # get the email address given subjectID
    my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
    for x in my_data.T:
        if x[0] == subjectID:
            return x[4]

def getPhone(subjectID): # get the phone number given subjectID
    my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
    for x in my_data.T:
        if x[0] == subjectID:
            #remove the a from the number, which is there to make it into a string because it overflows as an integer
            x[5] = x[5].translate(None, 'a')
            return x[5]

def contactResident(subjectID): #Contact the resident passed in through their preferred contact method
    my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
    for x in my_data.T:
        if x[0] == subjectID:
            #remove the a from the number, which is there to make it into a string because it overflows as an integer
            preferredContactMethod = x[6]
    if preferredContactMethod == 0:
        # Send a text message
        os.system('python GoogleVoice\\sendsms.py %s "You have a guest waiting in the lobby"' % getPhone(subjectID))
    elif preferredContactMethod == 1:
        #send out an email with the guest's image to the resident that lives in the apartment
        email = getEmail(subjectID)
        mail(email,
        "You have a visitor in the lobby",
        "Please see his or her attached image.",
        "Guest.jpg")
    elif preferredContactMethod == 2: #Call the resident
        engine.say('I will call the resident for you')
        engine.runAndWait()
        os.system('python GoogleVoice\\sendcall.py %s' % getPhone(subjectID))
        engine.say('Please pick up the phone to communicate')
        engine.runAndWait()
        time.sleep(60) # Wait 1 minute for the call to finish
    return subjectID

            
def listenAptEmail(): # listen for apartment number, returns email
    while True: # Run until it recognizes an apartment number
        winsound.Beep(500,200)
        with sr.Microphone() as source:
            audio = r.listen(source)
        winsound.Beep(400,200)
        
        try:
            word = r.recognize(audio)
            
            my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
            for x in my_data.T:
                if x[1] == word:
                    print "returned %s" % x[4]
                    return x[4]
        except LookupError:
            engine.say('Sorry?')
            engine.runAndWait()
            
def listenApt(): # listen apartment number, return ID number
    while True: # Run until it recognizes an apartment number or the word 'visiting'
        winsound.Beep(500,200)
        with sr.Microphone() as source:
            audio = r.listen(source)
        winsound.Beep(400,200)
        
        try:
            word = r.recognize(audio)
            
            my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
            for x in my_data.T:
                if x[1] == word:
                    print "returned %s" % x[0]
                    return x[0]
            if 'visiting' in word:
                print "You are a Guest"
                return -1
        except LookupError:
            engine.say('What did you say?')
            engine.runAndWait()

# This is for facial recognition, function from tutorial: http://hanzratech.in/2015/02/03/face-recognition-using-opencv.html
def get_images_and_labels(path):
    # Append all the absolute image paths in a list image_paths
    # We will not read the image with the .sad extension in the training set
    # Rather, we will use them to test our accuracy of the training
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.sad')]
    # images will contains face images
    images = []
    # labels will contains the label that is assigned to the image
    labels = []
    for image_path in image_paths:
        # Read the image and convert to grayscale
        image_pil = Image.open(image_path).convert('L')
        # Convert the image format into numpy array
        image = np.array(image_pil, 'uint8')
        # Get the label of the image
        nbr = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        # Detect the face in the image
        faces = faceCascade.detectMultiScale(image)
        # If face is detected, append the face to images and the label to labels
        for (x, y, w, h) in faces:
            images.append(image[y: y + h, x: x + w])
            labels.append(nbr)
    # return the images list and labels list
    return images, labels

# returns VERIFIED subject number    
def verify(nbr_predicted):
    print "at verify"
    print nbr_predicted
    my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
    for x in my_data.T: # find the person in question in the csv file by matching their IDs with their facial recognition ID
        if x[0] == nbr_predicted:
            print x
            engine.say('Are you %s?' % x[2])
            engine.runAndWait()
            if listenYN() == 0: #the person is not the resident we think it is from facial recognition, we may need to re-train
                engine.say('If you have an apartment number, please say it now, otherwise, say, visiting')
                engine.runAndWait()
                subjectID = listenApt()
                if subjectID == -1:
                    return -1
                for y in my_data.T:
                    if y[0] == subjectID:
                        engine.say('Are you %s?' % y[2])
                        engine.runAndWait()
                        if listenYN() == 1:
                            engine.say('Im sorry for confusing you %s, Ill do my best to identify you from now on' % y[2])
                            engine.runAndWait()
                            return y[0] # return VERIFIED subject number
                        else:
                            return -1 # -1 means guest
                            
            else: # we have the right person recognized
                return nbr_predicted

    # The nbr_predicted subject is not in our CSV file    
    engine.say('If you have an apartment number, please say it now, otherwise, say, visiting')
    engine.runAndWait()
    subjectID = listenApt()
    if subjectID == -1:
        return -1
    for y in my_data.T:
        if y[0] == subjectID:
            engine.say('Are you %s?' % y[2])
            engine.runAndWait()
            if listenYN() == 1:
                engine.say('Im sorry for confusing you %s, Ill do my best to identify you from now on' % y[2])
                engine.runAndWait()
                return y[0] # return VERIFIED subject number
            else:
                return -1 # -1 means guest
    return -1

# store the package
def pickupPackage(subjectID):
    engine.say('I am going to store it for the guest. Have a nice day.')
    engine.runAndWait()
    
    # Change the communication file to execute part 2 of the program, store package
    #fo = open("Web\\communication", "wb")
    #fo.write(subjectID);
    #fo.close()
                
    my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
    for x in my_data.T:
        if x[4] == getEmail(subjectID):
            print "This resident is being contacted: %s" % x
            x[3] = x[3] + 1
            print "Now: %s" % x
    np.savetxt("C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\database.csv", my_data, delimiter=',',fmt="%s")
    
    # wait until package is stored
    time.sleep(300) # TODO get real time
    return 0
    
# give a package to the resident
def deliverPackage(subjectID):
    engine.say('I have a package for you, please wait while I get it.')
    engine.runAndWait()
    
    # Change the communication file to execute part 2 of the program, give out package
    fo = open("Web\\communication", "wb")
    print "HERE ID:", subjectID
    fo.write(str(subjectID));
    fo.close()
    
    my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
    for x in my_data.T:
        if x[4] == getEmail(subjectID):
            x[3] = x[3] - 1
            print "Now: %s packages left in this persons mailbox" % x[3]
    np.savetxt("C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\database.csv", my_data, delimiter=',',fmt="%s")
    
    # wait until package is delivered
    time.sleep(300) # TODO get real time
    return 0
    
# run facial recognition
def rec():
    img = getImageFromURLorWebcam()
    imwrite("C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\inputImages\\subject00.jpg",img) #save image - is this del?
    imwrite("Guest.jpg",img) #save image

    path = 'C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\inputImages' #new line
    
    # A few lines below are from the Open CV Face Recognition tutorial at http://hanzratech.in/2015/02/03/face-recognition-using-opencv.html
    # Append the images with the extension .sad into image_paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')] #del? modify this line?
    for image_path in image_paths:
        predict_image_pil = Image.open(image_path).convert('L')
        predict_image = np.array(predict_image_pil, 'uint8')
        faces = faceCascade.detectMultiScale(predict_image)
        try:
            print faces[0]
        except:
            return 0
    
        # Only keep the biggest face (the closest one, in case there is a line)
        bigw = 0
        index = 0
        bigindex = 0
        for (x, y, w, h) in faces:
            print w
            if w > bigw:
                bigw = w
                bigIndex = index
            index = index + 1
        bigface = faces[bigIndex]
        print bigface
        print "BUT TOTAL BELOW:"
        print faces
        (x, y, w, h) = bigface
        if w < 80: # if the face is too small, the person is too far away, disqualify the face and quit the function
            return 0
        nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w])
         # please see how the dataset is arranged, it looks like subject**.# , where ** represents the subject number and # is the image number
         # to prevent duplicated
        nbr_actual = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        subjectID = verify(nbr_predicted)

        if subjectID == -1: # the person is a guest
            engine.say('Which apartment are you here to visit?')
            engine.runAndWait()
            
            # Contact the resident using his or her preferred contact method
            subjectIDVisited = contactResident(listenApt())
            
            engine.say('The resident has been notified that you are here')
            # Package delivery (the PR2 stores) is not activated
            #engine.say('Would you like to drop something off for the resident?')
            #engine.runAndWait()
            #if 1 == listenYN(): # the guest wants to drop something off for the resident
            #    print "Do stuff here"
            #    print "visiting this subject:", subjectIDVisited
            #    engine.say('Please place the package on the desk.')
            #    engine.runAndWait()
            #    time.sleep(2)

            #    pickupPackage(subjectIDVisited)
                
            #    return 0
            #else:  # the person does not want to drop something off for the resident
            engine.say('Have an awesome day.')
            engine.runAndWait()
            time.sleep(10)
        # The person is a resident, but we mis-recognized him.
        # Correct the dataset with new image and then deliver package if the resident has one
        elif subjectID != nbr_predicted:
            num = randint(1,3) # the logic of this is that people change over time, so it will overwrite previous images with 1/3 probability
            fileInitial = 'C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\ASA\\subject0{}.{}'.format(subjectID, 'jpeg')
            fileDest = 'C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\ASA\\subject0{}.{}'.format(subjectID, num)
            cv2.imwrite(fileInitial, predict_image[y: y + h, x: x + w])
            try:
                os.rename(fileInitial, fileDest)
            except:
                os.remove(fileDest)
                os.rename(fileInitial, fileDest)
                print "replaced entry"
                
            my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
            for x in my_data.T:
                if x[0] == subjectID:
                    if x[3] > 0:
                        deliverPackage(subjectID)
                    else:
                        engine.say('You have no packages in your mailbox.')
                        engine.runAndWait()
            engine.say('Have a wonderful day.')
            engine.runAndWait()
            time.sleep(10)
        # The person is a resident and we recognized him or her correctly. See if he or she has packages in storage and deliver one if the person does
        else:
            my_data = genfromtxt('database.csv',dtype=None,delimiter=',') #read in the database file into a numpy array
            for x in my_data.T:
                if x[0] == subjectID:
                    if x[3] > 0:
                        deliverPackage(subjectID)
                    else:
                        engine.say('You have no packages in your mailbox.')
                        engine.runAndWait()
            engine.say('Have a fantastic day.')
            engine.runAndWait()
            time.sleep(10)
    return 0

# >>>>>>>>>>>>>>>>>>>>>>>> End of Functions >>>>>>>>>>>>>>>>>>>>>>>>
# @@@@@@@@@@@@@@@@@@@@@@@ Start of Execution @@@@@@@@@@@@@@@@@@@@@@@

engine.say('Please wait')
engine.say('Im, learning faces from the facial recognition dataset')
engine.runAndWait()

# Path to the Dataset
path = 'C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\ASA'
# The images in the dataset are labeled by subject number
# Call the get_images_and_labels function and get the face images and the corresponding labels
images, labels = get_images_and_labels(path)
cv2.destroyAllWindows()

# Perform the training
recognizer.train(images, np.array(labels))

engine.say('The facial recognition engine has been trained')
engine.say('I am ready to greet guests')
engine.runAndWait()

# Greet residents in a loop
while True:
    if motionDetection() == 1: # if motion is detected,
        time.sleep(1)
        engine.say('May I help you?') # ask the person if he or she needs help
        engine.runAndWait()
        if listenYNTimeout() == 1: # if the response is 'yes,' go into facial recongition code
            engine.say('Say cheese!') # right before taking image used for facial recognition
            engine.runAndWait()
            rec()
        else:
            time.sleep(2)

# @@@@@@@@@@@@@@@@@@@@@@@ End of Execution @@@@@@@@@@@@@@@@@@@@@@@