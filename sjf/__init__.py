import sys, pprint
from termcolor import colored
from datetime import datetime
#import generator
import executor
from common import *

features = {
	# full feature list for version 1.0
	1: {
		'fuzz parameters':	True,	# fuzz command line parameters
		'fuzz stdin':		True,	#
		'fuzz env.vars':	True,	#
		'fuzz file':		True,	#
		'fuzz tcp server':	True,	#
		'fuzz tcp client':	False,	#
		'fuzz udp server':	False,	#
		'fuzz udp client':	False,	#
		'logging to file':	False,	#
		'documentation':	False	#
	},
	# 2.x features - refact required o_O
	2: {
		'read(n)/readln()':	False,	# to support multistage client-srv communications, complex protocols, etc 
		'ncurses ui':		False,	# don't look like shit
		'threads':			False,	# ... select()
		'client/srv mode':	False,	# run the same fuzz task on multiple machines
		'pcap import':		False,	# pcap import for tcp/udp client/server fuzzing
		'documentation':	False	#
	}
}
SW='jazzy'
VERSION_MAJOR=0
VERSION_MINOR=0

for mv in features:
	minor = 0
	for feature in features[mv]:
		if features[mv][feature]:
			minor += 1
	VERSION_MINOR = minor
	if minor == len(features[mv]):
		VERSION_MAJOR = mv
	else:
		break
SW_VERSION = "%s %d.%02d" % (SW, VERSION_MAJOR, VERSION_MINOR)
