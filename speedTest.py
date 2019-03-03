#coding:utf-8


import requests
import time
import threading
import socks
import socket
import sys
import logging
logger = logging.getLogger("Sub")

import speedtestnet
import fast
import cachefly


LOCAL_ADDRESS = "127.0.0.1"
LOCAL_PORT = 1087
DEFAULT_SOCKET = socket.socket

def setInfo(ADDRESS,PORT):
	LOCAL_ADDRESS = ADDRESS
	LOCAL_PORT = PORT

class SpeedTest(object):
	def __init__(self):
		self.__initSocket()

	#	self.__fileUrl = "http://speedtest.dallas.linode.com/100MB-dallas.bin" #100M File
	#	self.__proxy = {
	#		"http":"socks5://%s:%d" % (LOCAL_ADDRESS,LOCAL_PORT),
	#		"https":"socks5://%s:%d" % (LOCAL_ADDRESS,LOCAL_PORT)
	#	}
	#	self.__lock = threading.Lock()
	#	self.__sizeList = []

	def __initSocket(self):
		socket.socket = DEFAULT_SOCKET

	def startTest(self,method = "CACHE_FLY"):
		logger.info("Starting speed test with %s" % method)
		if (method == "SPEED_TEST_NET"):
			try:
				socks.set_default_proxy(socks.SOCKS5,LOCAL_ADDRESS,LOCAL_PORT)
				socket.socket = socks.socksocket
				logger.info("Initializing")
				s = speedtestnet.Speedtest()
				logger.info("Selecting Best Server.")
				logger.info(s.get_best_server())
				logger.info("Testing Download...")
				s.download()
				result = s.results.dict()
				self.__initSocket()
				return result["download"] / 8 #bits to bytes
			except:
				logger.exception("")
				return 0
		elif (method == "FAST"):
			try:
				fast.setProxy(LOCAL_ADDRESS,LOCAL_PORT)
				result = 0
				result = fast.fast_com(verbose=True)	
				#print(result)
				return result
			except:
				logger.exception("")
				return 0
		elif (method == "CACHE_FLY"):
			try:
				return cachefly.speedtestcachefly(LOCAL_PORT)
			except:
				logger.exception("")
				return 0
		elif (method == "SOCKET"):#Old speedtest
			try:
				return cachefly.speedtestsocket(LOCAL_PORT)
			except:
				logger.exception("")
				return 0

		else:
			raise Exception("Invalid test method %s" % method)

	def googlePing(self):
		logger.info("Testing latency to google.")
		return cachefly.pinggoogletest(LOCAL_PORT)

	def tcpPing(self,server,port):
		logger.info("Testing latency to server.")
		return cachefly.pingtcptest(server,port)

#Old Code
''' 
	def __progress(self,current,total):
		print("\r[" + "="*int(current/total * 20) + "] [%d%%/100%%]" % int(current/total * 100),end='')
		if (current >= total):
			print("\n",end="")


	def __download(self):
		size = 0
		starttime = time.time()
		chunkSize = 1024 * 512 #512 KBytes
		rep = requests.get(self.__fileUrl,proxies = self.__proxy,stream=True)
		totalSize = int(rep.headers["content-length"])
		for data in rep.iter_content(chunk_size = chunkSize):
			endtime = time.time()
			deltaTime = endtime - starttime
			size += len(data)
			if (deltaTime < 10):
				continue
			else:
				break
		if (self.__lock.acquire(timeout=5)):
			self.__sizeList.append(size)
			self.__lock.release()
		else:
			raise Exception("Could not acquire lock.")


	def testDownloadSpeed(self):
		size = 0
		print("Testing speed in 10s")
		threadList = []
		for i in range(0,4):
			t = threading.Thread(target=self.__download,args=())
			threadList.append(t)
			t.start()
		while (threading.active_count() > 1):
			print(threading.active_count())
			time.sleep(1)
		for item in self.__sizeList:
			size += item
		print (self.__sizeList)
	#	print(deltaTime)
		print(size)
		speed = size / 1024 / 1024 / 10
		if (speed < 1):
			return("%.2fKB" % (speed*1000))
		else:
			return("%.2fMB" % speed)

	def tcpPing(self):
		pass


	def testProgress(self):
		for i in range(0,51):
			self.__progress(i,50)
			time.sleep(0.25)
'''


if (__name__ == "__main__"):
	st = SpeedTest()
	#print(st.startTest("FAST")/1024/1024) #Fast Test Data : Speed in bytes/s
	#print(st.startTest("CACHE_FLY")) #CacheFly Test Data : Speed in bytes/s
	#print(st.startTest()) #Speed Test Data : Unknown
	#print(st.googlePing()) #Data : ms
	#print(st.tcpPing("114.114.114.114",53)) # Data : tunple (ping as s,data loss - 1)