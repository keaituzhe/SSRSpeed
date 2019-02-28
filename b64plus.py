#coding:utf-8

import base64

def fillb64(data):
	if (len(data) % 4):
		data += "=" * (4 - (len(data) % 4))
	return data

def encode(s):
	s = s.encode("utf-8")
	return base64.urlsafe_b64encode(s)

def decode(s):
	s = fillb64(s)
	return base64.urlsafe_b64decode(s)
