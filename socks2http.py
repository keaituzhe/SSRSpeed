#coding:utf-8
#Author:ranwen NyanChan

import socket
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
import struct
import select
import re
import traceback

compile_ipv4=re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
compile_ipv6=re.compile('(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))')

upstram_port=1087
def setUpstreamPort(port = 1087):
	global upstram_port
	upstram_port = port

def check_ipv4(host):
	if compile_ipv4.match(host.decode("utf-8")):
		return True
	return False
def check_ipv6(host):
	if compile_ipv6.match(host.decode("utf-8")):
		return True
	return False

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
	pass

class SocksProxy(StreamRequestHandler):

	def recvtrash(self,remote):
		remote.recv(3)
		ty=struct.unpack("!B",remote.recv(1))[0]
		if ty==1:
			remote.recv(4)
		elif ty==4:
			remote.recv(16)
		else:
			le=struct.unpack("!B",remote.recv(1))[0]
			remote.recv(le)
		remote.recv(2)
	def handle(self):

		# greeting header
		# read and unpack 2 bytes from a client
		ddt=self.connection.recv(1)
		typ=struct.unpack("!B",ddt)[0]
		if typ==5:
			remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			remote.connect(("127.0.0.1", upstram_port))
			remote.send(struct.pack("!B",5))
			self.exchange_loop(self.connection, remote)
			return 
		gg = ddt+self.connection.recv(4096)
		if gg[0:7]==b'CONNECT':
			#print("HTTPS")
			#print(gg)
			parstr=gg.split(b' ')[1]
			pos=parstr.rfind(b":")
			#(host,port)=parstr.split(b':')
			host=parstr[0:pos]
			port=parstr[pos+1:]
			port=int(port)
			#print(parstr)
			self.connection.send(b"HTTP/1.1 200\r\n\r\n")
			#print(host,port)
			remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			remote.connect(("127.0.0.1", upstram_port))
			remote.send(struct.pack("!BBB",5,1,0))
			remote.recv(2)
			if host[0:1]==b'[':
				host=host[1:len(host)-1]
			#print(host)
			#print(check_ipv4(host))
			if check_ipv4(host):
				remote.send(struct.pack("!BBBB4sH",5,1,0,1,socket.inet_aton(host.decode("utf-8")),port))
				self.recvtrash(remote)
				self.exchange_loop(self.connection, remote)
			elif check_ipv6(host):
				remote.send(struct.pack("!BBBB16sH",5,1,0,4,socket.inet_pton(socket.AF_INET6,host.decode("utf-8")),port))
				self.recvtrash(remote)
				self.exchange_loop(self.connection, remote)
			else:
				dat=struct.pack("!BBBBB",5,1,0,3,len(host))+host+struct.pack("!H",port)
				remote.send(dat)
				self.recvtrash(remote)
				self.exchange_loop(self.connection, remote)
		else:
			#print("HTTP")
			tmp=gg.split(b' ')[1].split(b'/')
			net=tmp[0]+b'//'+tmp[2]
			request=gg.replace(net,b'')
			#print(request)
			#print(gg)
			parstr=tmp[2]
			port=80
			pos=parstr.rfind(b":")
			if not pos==-1:
				host=parstr[0:pos]
				port=parstr[pos+1:]
				port=int(port)
			else:
				host=parstr
			#print(parstr)
			#print(host,port)
			remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			remote.connect(("127.0.0.1", upstram_port))
			remote.send(struct.pack("!BBB",5,1,0))
			remote.recv(2)
			if host[0:1]==b'[':
				host=host[1:len(host)-1]
			#print(host)
			#print(check_ipv4(host))
			if check_ipv4(host):
				remote.send(struct.pack("!BBBB4sH",5,1,0,1,socket.inet_aton(host.decode("utf-8")),port))
				self.recvtrash(remote)
				remote.send(request)
				self.exchange_loop(self.connection, remote)
			elif check_ipv6(host):
				remote.send(struct.pack("!BBBB16sH",5,1,0,4,socket.inet_pton(socket.AF_INET6,host.decode("utf-8")),port))
				self.recvtrash(remote)
				remote.send(request)
				self.exchange_loop(self.connection, remote)
			else:
				dat=struct.pack("!BBBBB",5,1,0,3,len(host))+host+struct.pack("!H",port)
				remote.send(dat)
				self.recvtrash(remote)
				remote.send(request)
				self.exchange_loop(self.connection, remote)


	def exchange_loop(self, client, remote):
		while True:
			try:
				r, w, e = select.select([client, remote], [], [])
				if client in r:
					data = client.recv(4096)
					if remote.send(data) <= 0:
						break
				if remote in r:
					data = remote.recv(4096)
					if client.send(data) <= 0:
						break
			except Exception:
				#traceback.print_exc()
				break

