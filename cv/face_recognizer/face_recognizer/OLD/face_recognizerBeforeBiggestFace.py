#!/usr/bin/python

# Import the required modules
import cv2, os
import numpy as np
from PIL import Image
import pdb
from cv2 import *

# initialize the camera
cam = VideoCapture(0)   # 0 -> index of camera
s, img = cam.read()
for x in range(0, 10):
    s, img = cam.read()
if s:    # frame captured without any errors
    namedWindow("cam-test",CV_WINDOW_AUTOSIZE)
    imshow("cam-test",img)
    cv2.waitKey(10)
    imwrite("C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\inputImages\\subject00.jpg",img) #save image

# For face detection we will use the Haar Cascade provided by OpenCV.
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

# For face recognition we will the the LBPH Face Recognizer 
recognizer = cv2.createLBPHFaceRecognizer()

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
            #cv2.imshow("Adding faces to traning set...", image[y: y + h, x: x + w])
            #cv2.waitKey(10)
    # return the images list and labels list
    return images, labels

# Path to the Yale Dataset
path = 'C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\ASA' #'/home/bikz05/Desktop/FaceRecognition/yalefaces'
# Call the get_images_and_labels function and get the face images and the 
# corresponding labels
images, labels = get_images_and_labels(path)
cv2.destroyAllWindows()

# Perform the tranining
recognizer.train(images, np.array(labels))

path = 'C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\inputImages' #new line

# Append the images with the extension .sad into image_paths
image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')] #modify this line
for image_path in image_paths:
    predict_image_pil = Image.open(image_path).convert('L')
    predict_image = np.array(predict_image_pil, 'uint8')
    faces = faceCascade.detectMultiScale(predict_image)
    try:
        print faces
    except:
        print "EXCEPTION!"

    # Only keep the biggest face (closest)
    bigw = 0
    index = 0
    for (x, y, w, h) in faces:
        print w
        if w > bigw:
            bigw = w
            bigIndex = index
        index = index + 1
    bigface = faces[bigIndex]
    print bigface
    for (x, y, w, h) in faces:
        nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w])
        nbr_actual = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        if nbr_predicted == 1:
            os.system('espeak -g 1 -p 60 -s 120 "Welcome home mister Moon"')
        elif nbr_predicted == 2:
            os.system('espeak -g 1 -p 60 -s 120 "Welcome home miss Kuhmeh"')
        elif nbr_predicted == 3:
            os.system('espeak -g 1 -p 60 -s 120 "Welcome home mister Chanfreau"')
        else:
            os.system('espeak -g 1 -p 60 -s 120 "What apartment number are you here to visit?"')
        cv2.imshow("Recognizing Face", predict_image[y: y + h, x: x + w])
        cv2.waitKey(2000)
        #cv2.imwrite("C:\\Users\\Agustin\\Desktop\\face_recognizer\\face_recognizer\\inputImages\\subject00.jpg", predict_image[y: y + h, x: x + w])
        break