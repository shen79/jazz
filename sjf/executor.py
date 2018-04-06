#!/usr/bin/python

import sys, os, binascii, subprocess, getopt, shlex, signal, time, yaml, socket
from common import *
import generator

def call(p):
#	dump(p)
	call = '_fuzz'
	if '-r' in p['opts']:
		call = '_replay'
	globals()[call](p)

def _exec(params):

#	dump(params)
	res = {
		'retcode': 0
	}
	ret = {
		'params': params,
		'result': {}
	}
# TCP service
	if params['cfg']['attack'] == 'tcpservice':
		host, port = params['cfg']['connect'].split(':')
		port = int(port)
		# BUG: if proc cannot bind or fail or something, the rest of the code wont know about it
		if params['command'] != '__skip__':
			proc = _popen(params['command'], env=params['env'])
		conn = _tcp_connect(host, port)
		if conn['retcode'] == 0:
			# connect success, sending trash
			conn['socket'].send(params['send'])
		conn['socket'].close()
		# TODO: check after testcase
		proc.wait()
		res['retcode'] = proc.returncode
# TCP client
	elif params['cfg']['attack'] == 'tcpclient':
		host, port = params['cfg']['listen'].split(':')
		port = int(port)
		server = _tcp_listen(host, port)
		proc = _popen(params['command'], env=params['env'])
		cli, cli_addr = server['socket'].accept()
		stdout, stderr = proc.communicate(input=params['stdin'])
		
		
# simple forkt - params, env, stdin
	else:
		sp = subprocess
		proc = _popen(params['command'], env=params['env'])
		stdout, stderr = proc.communicate(input=params['stdin'])
		proc.wait()
		res['retcode'] = proc.returncode
		res['stdout'] = stdout
		res['stderr'] = stderr
	ret['result'] = res
	return ret

def _popen(cmd, env):
	sp = subprocess
	proc = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=False, env=env)
	return proc

# _____ ____ ____    _     _     _             
#|_   _/ ___|  _ \  | |   (_)___| |_ ___ _ __  
#  | || |   | |_) | | |   | / __| __/ _ \ '_ \ 
#  | || |___|  __/  | |___| \__ \ ||  __/ | | |
#  |_| \____|_|     |_____|_|___/\__\___|_| |_|
# copy paste coz im too lazy, but its not important yet, just a temporary solution
def _tcp_listen(host, port):
	res = {
		'socket': None,
		'retcode': 0,
		'stderr': None
	}
	try:
		so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		so.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		so.bind((host, port))
		so.listen(1)
	except socket.error as e:
		die('listen fail :(')
	else:
		# connect success, sending trash
		res['retcode'] = 0
		res['socket'] = so
	
# _____ ____ ____     ____                            _   
#|_   _/ ___|  _ \   / ___|___  _ __  _ __   ___  ___| |_ 
#  | || |   | |_) | | |   / _ \| '_ \| '_ \ / _ \/ __| __|
#  | || |___|  __/  | |__| (_) | | | | | | |  __/ (__| |_ 
#  |_| \____|_|      \____\___/|_| |_|_| |_|\___|\___|\__|
def _tcp_connect(host, port):
	retrytimings = [.01, .05, .1, .1, .2, .2, .5, .5, 1, 1]
	res = {
		'socket': None,
		'retcode': 0,
		'stderr': None
	}
	for conn_attempt in range(0,10):
		try:
			so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			so.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			so.connect((host, port))
		except socket.error as e:
			# connect fail, maybe its something
			retryafter = retrytimings[conn_attempt]
#			dbg("Connect fail attempt:%d err:%d: %s (retry after %f)" % (conn_attempt+1, e.errno, e[1], retryafter))
			time.sleep(retryafter)
			res['retcode'] = e.errno
			res['stderr'] = e.message
		else:
			# connect success, sending trash
			res['retcode'] = 0
			res['socket'] = so
			break
	if conn_attempt == 9:
		res['stderr'] = 'too many connection failure... :('
#		err('too many connection failure... :(')
		res['socket'] = so
	return res
	
	

	

#
#  ____            _             
# |  _ \ ___ _ __ | | __ _ _   _ 
# | |_) / _ \ '_ \| |/ _` | | | |
# |  _ <  __/ |_) | | (_| | |_| |
# |_| \_\___| .__/|_|\__,_|\__, |
#           |_|            |___/ 

# TODO:  cleanup required
def _replay(params):
	msg("Replay mode")
	cfg = params['cfg']
	opts = params['opts']
	testcase_id = opts['-r']
	env = {}
	testcase_info = _get_testcase_info(testcase_id)
	fuzz_field_idx = testcase_info['field-idx']

	if cfg['attack'] == 'env':
		for idx, data in enumerate(cfg['fuzzdata']['fields']):
			if idx == fuzz_field_idx:
				env[data['name']] = testcase_info['pattern']
			else:
				env[data['name']] = data['value']
	else:
		env = params['env']

	fuzz_data = []
	for idx, data in enumerate(cfg['fuzzdata']['fields']):
		fuzz_data.append(cfg['fuzzdata']['fields'][idx]['value'])
	fuzz_data[testcase_info['field-idx']] = testcase_info['pattern']
	
	p = _build_fuzzdata({
		'cfg': cfg,
		'opts': opts,
		'command': ['__NOT_SET__'], 			# Req
		'stdin': '',
		'pattern': testcase_info['pattern'],
		'fuzz-field-idx': fuzz_field_idx,
		'env': env
	})
	rdata = _exec(p)
	dbg("Testcase ID: %s" % testcase_id)
	dbg('Generator: %s (%s)' % (testcase_info['generator-id'], testcase_info['generator-name']))
	dbg('Pattern len: %s' % len(testcase_info['pattern']))
#	dump(p)
	dump(rdata)


#  _____              _             
# |  ___|   _ _______(_)_ __   __ _ 
# | |_ | | | |_  /_  / | '_ \ / _` |
# |  _|| |_| |/ / / /| | | | | (_| |
# |_|   \__,_/___/___|_|_| |_|\__, |
#                             |___/ 

def _fuzz(params):
	msg("Fuzz mode")
	cfg = params['cfg']				# fuzzconfig file
	env = params['env']				# our env, default os.environ
	opts = params['opts']			# command line options

#	rcstats = {}					# return code counter
	fuzz_env_default = {}
	fuzz_env_keys = {}
	generators = generator.get()	# this will provide the patterns
	fuzz_fields = _get_fuzzfields(cfg['fuzzdata']['fields']) 	# a list containing the fuzzable indexes

	fuzz_default = [] 	# the fuzz "packet" with the default values
	for idx, data in enumerate(cfg['fuzzdata']['fields']):
		fuzz_default.append(cfg['fuzzdata']['fields'][idx]['value'])
# fields loop
	for fuzz_field_idx in fuzz_fields:
		fuzz_data = fuzz_default # not required for env
		fuzz_env = fuzz_env_default
		fuzz_field_name = cfg['fuzzdata']['fields'][idx]['name']
		fuzz_field_datatype = cfg['fuzzdata']['fields'][idx]['datatype']
		dbg('fuzzing param field #%d name:%s type:%s ' % (fuzz_field_idx, fuzz_field_name, fuzz_field_datatype))
# generators loop
		for generator_id in generators['by-gid']:
			generator_name = generators['by-gid'][generator_id]['name']
			generator_func = generators['by-gid'][generator_id]['func']
			generator_opts = generator_func(True)
			# we dont want to generate the whole fuckin list if the datatype is not suitable...
			if generator_opts['datatype'] != cfg['fuzzdata']['fields'][fuzz_field_idx]['datatype']: continue
			dbg('Generator: ' + generator_name)
			patterns = generator_func()
			pattern_num = len(patterns)-1
# patterns loop
			for pattern_idx, pattern in enumerate(patterns):
				testcase_id = "%s-%04x-%04x" % (generator_id, fuzz_field_idx, pattern_idx)			# generate a testcase ID for this testcase...
				sstr = "status %-42s %-32s %4d/%-4d \r" % (testcase_id, generator_name, pattern_idx, pattern_num) # ... and display it
				sys.stderr.write(sstr) # just some status for the users, to let em see whats happening
				# fuzz_data[fuzz_field_idx] = prefix + pattern + suffix
				p = _build_fuzzdata({
					'cfg': cfg,
					'opts': opts,
					'command': ['__NOT_SET__'], 			# Req
					'stdin': '',
					'env': env,
					'fuzz-field-idx': fuzz_field_idx,
					'pattern': pattern
				})
				rdata = _exec(p);
				if 'exit-on-signal' in cfg and rdata['result']['retcode'] == cfg['exit-on-signal']:
					_hit(testcase_id, rdata)
					dump(rdata)
					sys.exit(0)
				elif rdata['result']['retcode'] == -11:
					print ''
					_hit(testcase_id, rdata)
				elif rdata['result']['retcode'] == 255:
					print ''
					_interesting(testcase_id, rdata)
#				if rdata['result']['retcode'] not in rcstats: rcstats[rdata['result']['retcode']] = 0
#				rcstats[rdata['result']['retcode']] += 1
			print ''
				
				


def _build_fuzzdata(params):
	ret = params
	cfg = params['cfg']
	env = params['env']
	stdin = params['stdin']
	pattern = params['pattern']
	fuzz_field_idx = params['fuzz-field-idx']

	fuzz_data = []
	fuzz_env = {}
	for idx, field in enumerate(cfg['fuzzdata']['fields']):
		prefix, suffix = '', ''
		if 'prefix' in field: prefix = field['prefix']
		if 'suffix' in field: suffix = field['suffix']
#		dump(idx)
		if cfg['attack'] == 'env':
			if idx == fuzz_field_idx:
				fuzz_env.add({field['name']:prefix + pattern + suffix})
			else:
				fuzz_env.add({field['name']: prefix + field['value'] + suffix})
		else:
			if idx == fuzz_field_idx:
				fuzz_data.append(prefix + pattern + suffix)
			else:
				fuzz_data.append(prefix + field['value'] + suffix)

	if 'command' in cfg:
		params['command'] = cfg['command']
# Params
	if cfg['attack'] == 'params':		params['command'] = fuzz_data
# STDIN
	elif cfg['attack'] == 'stdin':		params['stdin'] = ''.join(fuzz_data)
# Environ
	elif cfg['attack'] == 'env':		params['env'] = fuzz_env
# Text File
	elif cfg['attack'] == 'textfile':
		params['file_contents'] = ''.join(fuzz_data)
		with open(cfg['file'], 'w') as f:
			f.write(params['file_contents'])
# TCP Service
	elif cfg['attack'] == 'tcpservice':
		params['command'] = '__skip__'
		params['send'] = ''.join(fuzz_data)
#		if 'command' in cfg:
#			params['command'] = cfg['command']
		params['connect'] = cfg['connect']
# TCP Client
	elif cfg['attack'] == 'tcpclient':
		params['send'] = ''.join(fuzz_data)
#		if 'command' in cfg:
#			params['command'] = cfg['command']
		params['listen'] = cfg['listen']
	else:
		die('unknown attack vector: %s' % cfg['attack'])

		pfx = ''
		if 'value' in field:
			pfx = field['value']
		if idx == params['field-idx']:
			ret += pfx + params['pattern']
		else:
			ret += field['value']
	return ret




def _hit(tcid, rdata):
	tcdata = _get_testcase_info(tcid)
	alert ("HIT: %s" % tcid)


def _interesting(tcid, rdata):
	tcdata = _get_testcase_info(tcid)
	msg("INTERESTING (hmmm): %s" % tcid)

def _get_fuzzfields(ffields):
	fuzz_idx = []
	for field_idx, field_data in enumerate(ffields):
		if field_data['variable'] == True:
			fuzz_idx.append(field_idx)
	return fuzz_idx

def _get_testcase_info(testcase_id):
	generator_id, fuzz_field_idx, pattern_idx = testcase_id.split('-')
	generators = generator.get()
	fuzz_field_idx = int(fuzz_field_idx, 16)
	pattern_idx = int(pattern_idx, 16)
	generator_name = generators['by-gid'][generator_id]['name']
	pattern = generators['by-gid'][generator_id]['func']()[pattern_idx]
	return {
		'generator-id': generator_id,
		'generator-name': generator_name,
		'field-idx': fuzz_field_idx,
		'pattern-idx': pattern_idx,
		'pattern': pattern
	}












































