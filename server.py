import socket
import threading

password = "/ebf734024jto485"
port = 8886

def server(conn, addr):
	try:
		file = open('mysql.log', 'rb')

		request = conn.recv(1024)
		method = request.split(' ')[0]
		src  = request.split(' ')[1]

		logfile = open("rms_server_log.txt","a")
		logfile.write('Connect by: ip=' + addr[0] + " port=" + str(addr[1]) + " url=" + src + "\n")
		logfile.close()

		if method == 'GET' and src == password:
			content = "HTTP/1.x 200 ok\r\nContent-Type: text/html\r\n\r\n"
			content += file.read()
			conn.sendall(content)

	except:
		print("Not Http Request or other error....")
	finally:
		file.close()
		conn.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', port))
sock.listen(1)


while True:
	conn, addr = sock.accept()
	threading.Thread(target=server,args=(conn, addr)).start()



	

	
