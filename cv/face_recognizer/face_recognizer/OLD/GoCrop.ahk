#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Sleep, 250
RunWait, python C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\DETECTFace\face_detect.py C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\inputImages\motion.jpg C:\Users\Agustin\Desktop\face_recognizer\face_recognizer\DETECTFace\haarcascade_frontalface_default.xml
