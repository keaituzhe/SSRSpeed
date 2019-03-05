#coding:utf-8

import sys
import os 
import time
import logging
logger = logging.getLogger("Sub")

from exportResult import exportAsPng,exportAsJson
from shadowsocksR import SSRParse,SSR
from speedTest import SpeedTest,setInfo
import importResult

class ConsoleUi(object):
	def __init__(self):
		self.__ssrp = SSRParse()
		self.__ssr = SSR()
		self.__method = "FAST"
		self.__config = {}
		self.__result = []
		self.__retryList = []
		self.__retryConfig = []

	def __showHelp(self):
		logger.info("Show Console Help.")
		print("Options: ")
		print("	h\n	         Show this message.")
		print("	c CONFIG_FILE\n	         Import shadowsocksr config from config file.")
		print("	u URL\n	         Import shadowsocksr config from subscription link.")
		print("	m METHOD\n	         Select test medhod in speedtestnet,fast and cachefly.")
		print("	f KEYWORD\n	         Filter nodes by group and remarks using keyword.")
		print("	fr KEYWORD\n	         Filter nodes by remarks using keyword.")
		print("	fg KEYWORD\n	         Filter nodes by group using keyword.")
		print("	l\n	         Show nodes in the list.")
		print("	t\n	         Start test.")
		print("	e TYPE\n	         Export test result to json or png file,now supported 'png' or 'json'")
		print("	i FILENAME\n	         Import test result from json file and export it.")
		print("	q\n	         Exit.")
		print("")

	def run(self):
		print("type 'h' for help.")
		while (True):
			cmds = input("> ")
			logger.debug("User input : '%s'" % str(cmds))
			cmdList = cmds.split(" ")
			cmd = cmdList[0]
			if (cmd == "h"):
				self.__showHelp()
				continue
			elif(cmd == "c"):
				self.__ssrp.readGuiConfig(cmdList[1])
				continue
			elif(cmd == "u"):
				self.__ssrp.readreadSubscriptionConfig(cmdList[1])
				continue
			elif(cmd == "m"):
				if (cmdList[1] == "speedtestnet"):
					self.__method = "SPEED_TEST_NET"
				elif(cmdList[1] == "fast"):
					self.__method = "FAST"
				elif(cmdList[1] == "cachefly"):
					self.__method == "CACHE_FLY"
				else:
					logger.error("Invalid test method,using default: fast")
				logger.info("Test method set : %s" % self.__method)
				continue
			elif(cmd == "f"):
				self.__ssrp.filterNode(cmdList[1])
				continue
			elif(cmd == "fr"):
				self.__ssrp.filterNode("","",cmdList[1])
				continue
			elif(cmd == "fg"):
				self.__ssrp.filterNode("",cmdList[1])
				continue
			elif(cmd == "l"):
				self.__ssrp.printNode()
				continue
			elif(cmd == "t"):
				retryMode = False
				config = self.__ssrp.getNextConfig()
				while (True):
					_item = {}
					_item["group"] = config["group"]
					_item["remarks"] = config["remarks"]
					self.__ssr.startSsr(config)
					logger.info("Starting test for %s - %s" % (_item["group"],_item["remarks"]))
					time.sleep(1)
					try:
						st = SpeedTest()
						latencyTest = st.tcpPing(config["server"],config["server_port"])
						time.sleep(1)
						#_thread.start_new_thread(socks2httpServer.serve_forever,())
						#logger.debug("socks2http server started.")
						_item["dspeed"] = st.startTest(self.__method)
						time.sleep(0.2)
						self.__ssr.stopSsr()
						time.sleep(0.2)
						self.__ssr.startSsr(config)
					#	.print (latencyTest)
						_item["loss"] = 1 - latencyTest[1]
						_item["ping"] = latencyTest[0]
					#	_item["gping"] = st.googlePing()
						_item["gping"] = 0
						if ((int(_item["dspeed"]) == 0) and (retryMode == False)):
							self.__retryList.append(_item)
							self.__retryConfig.append(config)
						else:
							self.__result.append(_item)
						logger.info("%s - %s - Loss:%s%% - TCP_Ping:%d - Google_Ping:%d - Speed:%.2f" % (_item["group"],_item["remarks"],_item["loss"] * 100,int(_item["ping"] * 1000),int(_item["gping"] * 1000),_item["dspeed"] / 1024 / 1024) + "MB")
						#socks2httpServer.shutdown()
						#logger.debug("Socks2HTTP Server already shutdown.")
					except Exception:
						self.__ssr.stopSsr()
						#socks2httpServer.shutdown()
						#logger.debug("Socks2HTTP Server already shutdown.")
						#traceback.print_exc()
						logger.exception("")
						sys.exit(1)
					self.__ssr.stopSsr()
					if (retryMode):
						if (self.__retryConfig != []):
							config = self.__retryConfig.pop(0)
						else:
							config = None
					else:
						config = self.__ssrp.getNextConfig()

					if (config == None):
						if ((retryMode == True) or (self.__retryList == [])):
							break
						ans = str(input("%d node(s) got 0kb/s,do you want to re-test these node? (Y/N)" % len(self.__retryList))).lower()
						if (ans == "y"):
							#	logger.debug(retryConfig)
							retryMode = True
							config = self.__retryConfig.pop(0)
						#	logger.debug(config)
							continue
						else:
							for r in self.__retryList:
								self.__result.append(r)
							break
				continue
			elif(cmd == "e"):
				if (cmdList[1] == "json"):
					exportAsJson(self.__result)
				elif(cmdList[1] == "png"):
					exportAsPng(self.__result)
				else:
					exportAsJson(self.__result)
				continue
			elif (cmd == "i"):
				self.__result = importResult.importResult(cmdList[1])
				continue
			elif (cmd == "q"):
				break
			else:
				logger.error("Invalid command %s" % cmd)


