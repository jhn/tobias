#!/usr/bin/python
 
import sys		#for cmd line argv
import time		#for delay
import pygst		#for playing mp3 stream
import gst		# " "
 
#take command line args as the input string
input_string = sys.argv
#remove the program name from the argv list
input_string.pop(0)
 
#convert to google friendly url (with + replacing spaces)
tts_string = '+'.join(input_string)
 
print tts_string
 
#use string in combination with the translate url as the stream to be played
music_stream_uri = 'http://translate.google.com/translate_tts?q=' + tts_string
player = gst.element_factory_make("playbin", "player")
player.set_property('uri', music_stream_uri)
player.set_state(gst.STATE_PLAYING)
 
#requires a delay, if the py process closes before the mp3 has finished it will be cut off.
time.sleep(12)