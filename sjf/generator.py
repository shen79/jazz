from md5 import new as _md5_new
import struct
#from md5 import md5 as _

generators = {
	'by-gid': {},
	'by-name': {}
}
_t_string =  {'binary': True, 'string': False, 'number': False}
_t_binary =  {'binary': True, 'string': False, 'number': False}
_t_number =  {'binary': False, 'string': False, 'number': True}


def _register(name):
	gid = _md5_new(name).hexdigest()
	func = eval(name)
	opts = func(True)
	generators['by-gid'][gid] = {'name': name, 'func': func, 'opts': opts}
	generators['by-name'][name] = {'gid': gid, 'func': func, 'opts': opts}


#
# String generators
#
def gen_single(opts=False):
	"""Single characters from 1 to 255"""
	if opts: return {
		'datatype': 'string'
	}
	ret = []
	for cc in range(1, 256):
		ret.append(chr(cc))
	return ret

def gen_fmtstr(opts=False):
	"""Format string patterns with different length"""
	if opts: return {
		'datatype': 'string'
	}
	ret = []
	fschars = 'csdioxXufFeEaAgGnp'
	maxpow = 6
	maxpchar = 4
	for char in fschars:
		for p in range(1, maxpchar+1):
			pchar = '%'*p
			for i in range(0, maxpow):
				ret.append((pchar+char)*2**i)
	return ret

def gen_length(opts=False):
	"""Strings with different characters (except 0), length is (char*2**i)"""
	if opts: return {
		'datatype': 'string'
	}
	ret = []
	maxpow = 16
	for byte in gen_single():
		for i in range(0, maxpow):
			ret.append(byte*2**i)
	return ret


def gen_number_as_string(opts=False):
	"""TODO"""
	if opts: return {'datatype': 'string'}
	return ["%d" % 2**i for i in range(0, 256)]

def gen_number_as_string_hex(opts=False):
	"""TODO"""
	if opts: return {'datatype': 'string'}
	return ["%x" % 2**i for i in range(0, 256)]

#
# Number generators
#

def _gen_number(pack, start=0, end=256, step=1):
	return [struct.pack(pack, i) for i in range(start, end, step)]

def gen_number_byte(opts=False):
	"""TODO generates"""
	if opts: return {'datatype': 'number'}
	return _gen_number('<B', 0, 256, 1)


def gen_number_word(opts=False):
	"""TODO generates"""
	if opts: return {'datatype': 'number'}
	ret = _gen_number('<L', 0, 0xffff+1, 256)
	ret+= _gen_number('>L', 0, 0xffff+1, 256)
	return ret

def gen_number_dword(opts=False):
	"""TODO generates"""
	if opts: return {'datatype': 'number'}
	ret = _gen_number('<L', 0, 0xffffffff+1, 0xfffff+1)
	ret+= _gen_number('>L', 0, 0xffffffff+1, 0xfffff+1)
	return ret


#
# Binary generators
#





def get():
	import common
	import generator
	for obj in dir(generator):
		if obj[0:4] == 'gen_':
			_register(obj)
#	common.dump(generators)
	return generators


if __name__ == '__main__':
	import sys
	gen = get()
	if len(sys.argv) == 1:
		for fn in gen['by-name']:
			f = gen['by-name'][fn]
			#flags = [fl for fl in f['flags'] if f['flags'][fl]]
			print "generator: %s\n\tg.id: %s\n\topts: %s\n\tinfo: %s" % (fn, f['gid'], f['opts'], f['func'].__doc__)
	else:
		for p in gen['by-name'][sys.argv[1]]['func']():
			print p
























	