import sys, pprint, inspect, yaml
from termcolor import colored
from datetime import datetime


def _out(msg, clr, atr=''):
	time = datetime.now().__str__()[11:19]
	time = colored(time, 'blue')

	stack = [d[3] for d in inspect.stack()][::-1]
	stack = ' ' + ('|'.join(stack[1:-1])) + ': '
	stack = colored(stack, 'grey')

	if atr == '':	msg = colored(msg, clr)
	else:			msg = colored(msg, clr, attrs=[atr])

	print time + stack + msg

def dbg(s):		_out(pprint.pformat(s), 'blue','')
def dump(s):
	s = "\n" + yaml.dump(s)
	_out(s, 'white','')

def msg(s):		_out(s, 'white', '')
def hdr(s):		_out(s, 'yellow', '')
def info(s):	_out(s, 'blue', 'bold')
def alert(s):	_out(s, 'red', 'bold')
def grey(s):	_out(s, 'grey', '')
def err(s):		_out(s, 'red', '')
def die(s):
	_out(s, 'yellow', 'reverse')
	sys.exit(1)


