#!/usr/bin/python
import parser
import os
import os.path

HAND_HISTORY_PATH = "/home/msharman/HandHistory/antler88"

for f in os.listdir( HAND_HISTORY_PATH ):
    path = os.path.join( HAND_HISTORY_PATH, f )
    try:
	print "Parsing %s:"%f
        parser.parseFile( path  )
    except Exception as e:
        print "Exception parsing %s: %s"%(f,e)
        exit()
