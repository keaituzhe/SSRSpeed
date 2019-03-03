#coding:utf-8
#Author:ranwen NyanChan

from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
import time
import socket
import struct
import threading
import requests
import logging
logger = logging.getLogger("Sub.CacheFly")


FLAG=False
ATI=0
ATR=0
lock=threading.Lock()
MXTI=10
THR=4
USE_SOCKS=True
SOCKS_PORT=1080


def testsocketthr():
    global FLAG,ATI,ATR
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if USE_SOCKS:
        s.connect(("127.0.0.1",SOCKS_PORT))
        s.send(b"\x05\x01\x00")
        s.recv(2)
        s.send(b"\x05\x01\x00\x03\x15cachefly.cachefly.net\x00\x50")
        s.recv(10)
    else:
        s.connect(("cachefly.cachefly.net",80))
    s.send(b"GET /100mb.test HTTP/1.1\r\nHost: cachefly.cachefly.net\r\nUser-Agent: curl/11.45.14\r\n\r\n")
    mxv=100*1024*1024
    st=time.time()
    nmsl=0
    while True:
        xx=s.recv(4096)
        logger.debug(xx)
        nmsl+=len(xx)
        if nmsl>=mxv or FLAG:
            break
    FLAG=1
    ed=time.time()
    s.close()
    lock.acquire()
    logger.debug(nmsl)
    logger.debug(ed-st)
    ATI+=nmsl
    #ATR+=ed-st
    ATR=max(ATR,ed-st)
    lock.release()

#if __name__ == '__main__':
#    for i in range(0,THR):
#        xx=threading.Thread(target=test1)
#        xx.start()
#    time.sleep(MXTI)
#    FLAG=True
#    time.sleep(0.1)
#    print(ATI)
#    print(ATR)
#    print(ATI/ATR*THR)
#    print(ATI/ATR*THR*8)

def speedtestsocket(port=1080):#old speedtest
    global SOCKS_PORT,ATI,ATR,FLAG
    SOCKS_PORT=port
    ATI=0
    ATR=0
    FLAG=False
    for i in range(0,THR):
        xx=threading.Thread(target=testsocketthr)
        xx.start()
    cas=int(MXTI/0.1)
    for i in range(0,cas):
        time.sleep(0.1)
        if FLAG:
            break
    FLAG=True
    for i in range(0,10):
        time.sleep(0.1)
        if ATR!=0:
            break
    if ATR==0:
        ATR=1
        print("ERROR please retry")
    return ATI/ATR
    #return ATI/ATR*THR

class SpeedTest(object):
    def __init__(self,LOCAL_PORT=1080,maxtime=15,thread=8,testfile="http://cachefly.cachefly.net/100mb.test"):
        self.__fileUrl = testfile
        self.__thread=thread
        self.__proxy = {
            "http":"socks5h://%s:%d" % ("127.0.0.1",LOCAL_PORT),
            "https":"socks5h://%s:%d" % ("127.0.0.1",LOCAL_PORT)
        }
        self.nowsp=[]
        self.mxt=maxtime
        self.mxs=0
        for i in range(0,thread):
            self.nowsp.append(0)

    def __progress(self,current,total):
        nows=0
        for i in range(0,self.__thread):
            nows+=self.nowsp[i]
        self.mxs=nows
        print("\r[" + "="*int(current/total * 20) + "] [%d%%/100%%] %dK/s" % (int(current/total * 100),int(nows/1024)),end='')
        if (current >= total):
            print("\n",end="")
    
    def testthread(self,thid):
        logger.debug("Thread %d" % thid)
        size = 0
        starttime = time.time()
        chunkSize = 1024 * 4 #4 KBytes
        try:
            req = requests.get(self.__fileUrl,proxies = self.__proxy,stream=True,headers={"User-Agent":"curl/11.45.14"})
            #req = requests.get(self.__fileUrl,stream=True)
            totalSize = int(req.headers["content-length"])
            stsiz=0
            sttim=0
            for data in req.iter_content(chunk_size = chunkSize):
                endtime = time.time()
                deltaTime = endtime - starttime
                size += len(data)
                if deltaTime>=0.4:
                    if stsiz==0:
                        stsiz=size
                        sttim=time.time()
                    else:
                        self.nowsp[thid]=(size-stsiz)/(endtime-sttim)
                logger.debug(self.nowsp[thid])
                logger.debug(len(data),(endtime-lastime))
                logger.debug(data)
                if (deltaTime >= self.mxt):
                    logger.debug(deltaTime,self.mxt)
                    break
            self.nowsp[thid]=(size-stsiz)/(endtime-sttim)
            logger.debug(size)
            logger.debug(size/deltaTime)
        except:
            return

    def testDownloadSpeed(self):
        #print("Testing Speed")
        self.mxs=0
        for i in range(0,self.__thread):
            x=threading.Thread(target=self.testthread,args=(i,))
            x.start()
        times=int(self.mxt/0.2+1)
        for i in range(0,times):
            self.__progress(i,times-1)
            time.sleep(0.2)
        logger.debug(self.mxs)
        return self.mxs

    def tcpPing(self):
        pass

def speedtestcachefly(port=1080):
    x=SpeedTest(port)
    return x.testDownloadSpeed()

if __name__ == '__main__':
    print(speedtestcachefly())

def pingtcptest(host,port):
    alt=0
    suc=0
    fac=0
    while suc<5 and fac<5:
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            st=time.time()
            s.settimeout(3)
            s.connect((host,port))
            s.close()
            alt+=time.time()-st
            suc+=1
        except Exception as err:
            logger.exception("TCP Ping Exception:")
            fac+=1
    if suc==0:
        return (0,0)
    return (alt/suc,suc/(suc+fac))

def pinggoogletest(port=1080):
    alt=0
    for i in range(0,2):
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect(("127.0.0.1",port))
            st=time.time()
            s.send(b"\x05\x01\x00")
            s.recv(2)
            s.send(b"\x05\x01\x00\x03\x0agoogle.com\x00\x50")
            s.recv(10)
            s.send(b"GET / HTTP/1.1\r\nHost: google.com\r\nUser-Agent: curl/11.45.14\r\n\r\n")
            s.recv(1)
            s.close()
            alt+=time.time()-st
        except Exception as err:
            logger.exception("Google Ping Exception:")
            alt+=10000
    return alt/2
