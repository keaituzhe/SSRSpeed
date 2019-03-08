#coding:utf-8

import json
import requests
import subprocess
import platform
import os
import sys
import logging
logger = logging.getLogger("Sub")

import b64plus

LOCAL_ADDRESS = "127.0.0.1"
LOCAL_PORT = 1087
TIMEOUT = 10

class SSR(object):
	def __init__(self):
		self.__config = {}
		self.__process = None

	def __checkPlatform(self):
		tmp = platform.platform()
		if ("Windows" in tmp):
			return "Windows"
		elif("Linux" in tmp):
			return "Linux"
		else:
			return "Unknown"

	def startSsr(self,config):
		self.__config = config
		self.__config["server_port"] = int(self.__config["server_port"])
		with open("./config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(self.__config))
			f.close()
		if (self.__process == None):
			if (self.__checkPlatform() == "Windows"):
				if (logger.level == logging.DEBUG):
					print("DEBUG")
					self.__process = subprocess.Popen(["python","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()])
				else:
					self.__process = subprocess.Popen(["python","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			elif(self.__checkPlatform() == "Linux"):
				if (logger.level == logging.DEBUG):
					self.__process = subprocess.Popen(["python3","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()])
				else:
					self.__process = subprocess.Popen(["python3","./shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			else:
				logger.error("Your system does not supported.Please contact developer.")
				sys.exit(1)
			logger.info("Starting ShadowsocksR with server %s:%d" % (config["server"],config["server_port"]))

		#	print(self.__process.returncode)


	def stopSsr(self):
		if(self.__process != None):
			self.__process.terminate()
	#		print (self.__process.returncode)
			self.__process = None
			logger.info("ShadowsocksR terminated.")
	#	self.__ssrProcess.terminate()


class SSRParse(object):
	def __init__(self):
		self.__configList = []

	def __parseLink(self,link):
		decoded = b64plus.decode(link).decode("utf-8")
		decoded1 = decoded.split("/?")[0].split(":")
		decoded2 = decoded.split("/?")[1].split("&")
		_config = {
			"server":decoded1[0],
			"server_port":decoded1[1],
			"method":decoded1[3],
			"protocol":decoded1[2],
			"obfs":decoded1[4],
			"password":b64plus.decode(decoded1[5]).decode("utf-8"),
			"protocol_param":"",
			"obfsparam":"",
			"remarks":"",
			"group":""
		}
		for ii in decoded2:
			if ("obfsparam" in ii):
				_config["obfs_param"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif ("protocolparam" in ii):
				_config["protocol_param"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif ("remarks" in ii):
				_config["remarks"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif("group" in ii):
				_config["group"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
		_config["local_port"] = LOCAL_PORT
		_config["local_address"] = LOCAL_ADDRESS
		_config["timeout"] = TIMEOUT
		_config["fast_open"] = False
		return _config

	def __filterGroup(self,gkw):
		_list = []
		if (gkw == ""):return
		for item in self.__configList:
			if (gkw in item["group"]):
				_list.append(item)
		self.__configList = _list

	def __filterRemark(self,rkw):
		_list = []
		if (rkw == ""):return
		for item in self.__configList:
			if (rkw in item["remarks"]):
				_list.append(item)
		self.__configList = _list

	def filterNode(self,kw = "",gkw = "",rkw = ""):
		_list = []
		if (kw != ""):
			for item in self.__configList:
				if ((kw in item["group"]) or (kw in item["remarks"])):
					_list.append(item)
			self.__configList = _list
		self.__filterGroup(gkw)
		self.__filterRemark(rkw)

	def __excludeGroup(self,gkw):
		_list = []
		if (gkw == ""):return
		for item in self.__configList:
			if (gkw not in item["group"]):
				_list.append(item)
		self.__configList = _list

	def __excludeRemark(self,rkw):
		_list = []
		if (rkw == ""):return
		for item in self.__configList:
			if (rkw not in item["remarks"]):
				_list.append(item)
		self.__configList = _list

	def excludeNode(self,kw = "",gkw = "",rkw = ""):
	#	print((kw,gkw,rkw))
		_list = []
		if (kw != ""):
			for item in self.__configList:
				if ((kw not in item["group"]) and (kw not in item["remarks"])):
					_list.append(item)
			self.__configList = _list
		self.__excludeGroup(gkw)
		self.__excludeRemark(rkw)

	def printNode(self):
		for item in self.__configList:
			#print("%s - %s" % (item["group"],item["remarks"]))
			logger.info("%s - %s" % (item["group"],item["remarks"]))

	def readSubscriptionConfig(self,url):
		header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}
		rep = requests.get(url,headers = header).content.decode("utf-8")
		linksArr = (b64plus.decode(rep).decode("utf-8")).split("\n")
		for link in linksArr:
			link = link.strip()
			if (link[:6] != "ssr://"):continue
			link = link[6:]
			self.__configList.append(self.__parseLink(link))

		logger.info("Read %d node(s)" % len(self.__configList))
			
	def readGuiConfig(self,filename):
		with open(filename,"r",encoding="utf-8") as f:
			for item in json.load(f)["configs"]:
				_dict = {
					"server":item["server"],
					"server_port":item["server_port"],
					"password":item["password"],
					"method":item["method"],
					"protocol":item["protocol"],
					"protocol_param":item["protocolparam"],
					"obfs":item["obfs"],
					"obfs_param":item["obfsparam"],
					"remarks":item["remarks"],
					"group":item["group"],
					"local_address":LOCAL_ADDRESS,
					"local_port":LOCAL_PORT,
					"timeout":TIMEOUT,
					"fast_open": False
				}
				self.__configList.append(_dict)
			f.close()

		logger.info("Read %d node(s)" % len(self.__configList))

	def getNextConfig(self):
		if (self.__configList != []):
			return self.__configList.pop(0)
		else:
			return None




