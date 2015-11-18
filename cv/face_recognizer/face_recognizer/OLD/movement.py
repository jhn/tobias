import cv2
import os
import time
def diffImg(t0, t1, t2):
    d1 = cv2.absdiff(t2, t1)
    d2 = cv2.absdiff(t1, t0)
    return cv2.bitwise_and(d1, d2)
    
def motionDetection():

    cam = cv2.VideoCapture(0)  
    
    winName = "Movement Indicator"
    cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)
    
    # Read three images first:
    t_minus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
    t = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
    t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
    dst = 0
    while True:
        cv2.imshow( winName, diffImg(t_minus, t, t_plus) )
    
        dst = cv2.absdiff(t_minus, t)
        dst = dst.sum()
        if dst > 800000:
            time.sleep(2)
            os.system('python face_recognizer.py')
            exit()
    
        # Read next image
        t_minus = t
        t = t_plus
        t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
                
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyWindow(winName)


motionDetection()