#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; Delete all previous images - fresh start
dir = C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\inputImages
FileDelete, %dir%\*.jpg

; Run Motion detection software
Run, Yawcam.exe, C:\Program Files\Yawcam

;MsgBox, WAIT TILL TAKE PICTURE(s) - increase imgs/second?

;This stuff below should run in a loop

; RunWait, C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\DETECT AND CROP\SNFaceCrop -d C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\inputImages -f *.jpg -ex 0 -ey 20
RunWait, python C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\DETECTFace\face_detect.py C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\inputImages\motion.jpg C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\DETECTFace\haarcascade_frontalface_default.xml

MsgBox, IS IT ACTUALLY DONE ALREADY? now delete files xml and on previous directory - close the program - run the python program already trained on training data

;dir = C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\inputImages
;FileDelete, %dir%\*.jpg