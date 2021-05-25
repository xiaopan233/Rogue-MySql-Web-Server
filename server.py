import socket


password = "/ebf734024jto485"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 8886))
sock.listen(100)

while True:
# maximum number of requests waiting
	conn, addr = sock.accept()
	request = conn.recv(1024)
	method = request.split(' ')[0]
	src  = request.split(' ')[1]
	logfile = open("rms_server_log.txt","a")
	logfile.write('Connect by: ip=' + addr[0] + " port=" + str(addr[1]) + " url=" + src + "\n")
	logfile.close()

	#deal wiht GET method
	if method == 'GET':
		if src == password:
			content = "HTTP/1.x 200 ok\r\nContent-Type: text/html\r\n\r\n"
			file = open('mysql.log', 'rb')
			content += file.read()
			file.close()
		else:
			conn.close()
			continue
	else:
		conn.close()
		continue

	conn.sendall(content)
	#close connection
	conn.close()
