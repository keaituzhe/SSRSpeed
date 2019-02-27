#coding:utf-8

from PIL import Image,ImageDraw,ImageFont
import json
import os
import sys
import time

'''
	resultJson
		{
			"group":"GroupName",
			"remarks":"Remarks",
			"loss":0,#Data loss (0-1)
			"ping":0.014,
			"gping":0.011,
			"dspeed":12435646 #Bytes
		}
'''

def exportAsPng(result):
	imageHeight = len(result) * 30 + 30
	resultImg = Image.new("RGB",(780,imageHeight),(255,255,255))
	resultFont = ImageFont.truetype("msyh.ttc",18)
	draw = ImageDraw.Draw(resultImg)

	draw.line((0,0,0,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((160,0,160,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((520,0,520,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((580,0,580,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((640,0,640,imageHeight - 1),fill=(127,127,127),width=1)
	draw.line((700,0,700,imageHeight - 1),fill=(127,127,127),width=1)
	draw.text((5,4),"Group",font=resultFont,fill=(0,0,0))
	draw.text((165,4),"Remarks",font=resultFont,fill=(0,0,0))
	draw.text((525,4),"Loss",font=resultFont,fill=(0,0,0))
	draw.text((585,4),"Ping",font=resultFont,fill=(0,0,0))
	draw.text((645,4),"GPing",font=resultFont,fill=(0,0,0))
	draw.text((705,4),"DSpeed",font=resultFont,fill=(0,0,0))
	draw.line((0,30,779,30),fill=(127,127,127),width=1)

	for i in range(0,len(result)):
		draw.line((0,30 * i + 60,779,30 * i + 60),fill=(127,127,127),width=1)
		item = result[i]
		group = item["group"]
		
		while (draw.textsize(group,font=resultFont)[0] > 150):
			group = group[:-1]
		draw.text((5,30 * i + 30 + 4),group,font=resultFont,fill=(0,0,0))

		remarks = item["remarks"]
		while (draw.textsize(remarks,font=resultFont)[0] > 350):
			remarks = remarks[:-1]
		draw.text((165,30 * i + 30 + 4),remarks,font=resultFont,fill=(0,0,0,0))

		loss = str(item["loss"] * 100) + "%%"
		while(draw.textsize(loss,font=resultFont)[0] > 50):
			loss = loss[:-1]
		draw.text((525,30 * i + 30 + 4),loss,font=resultFont,fill=(0,0,0))

		ping = str(item["ping"] * 1000)
		while(draw.textsize(ping,font=resultFont)[0] > 50):
			ping = ping[:-1]
		draw.text((585,30 * i + 30 + 4),ping,font=resultFont,fill=(0,0,0))

		gping = str(item["gping"] * 1000)
		while(draw.textsize(gping,font=resultFont)[0] > 50):
			gping = gping[:-1]
		draw.text((645,30 * i + 30 + 4),gping,font=resultFont,fill=(0,0,0))

		speed = item["dspeed"]
		draw.rectangle((701,30 * i + 30 + 1,779,30 * i + 60 -1),getColor(speed))
		draw.text((705,30 * i + 30 + 1),parseSpeed(speed),font=resultFont,fill=(0,0,0))
		
	filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".png"
	resultImg.save(filename)
	print("Result image saved as %s" % filename)

def parseSpeed(speed):
	speed = speed / 1024 / 1024
	if (speed < 1):
		return("%.2fKB" % (speed * 1024))
	else:
		return("%.2fMB" % speed)

def mixColor(lc,rc,rt):
	return (int(lc[0]*(1-rt)+rc[0]*rt),int(lc[1]*(1-rt)+rc[1]*rt),int(lc[2]*(1-rt)+rc[2]*rt))

def getColor(data):
	if (data > 100 * 1024 * 1024):
		return (255,0,0)
	elif (data < 64 * 1024):
		return mixColor((255,255,255),(128,255,0),data/64/1024)
	elif (data < 512 * 1024):
		return mixColor((128,255,0),(255,255,0),(data-64*1024)/(512*1024-64*1024))
	elif (data < 4*1024*1024):
		return mixColor((255,255,0),(255,128,192),(data-512*1024)/(4*1024*1024-512*1024))
	else:
		return mixColor((255,128,192),(255,0,0),(data-16*1024*1024)/((100-16)*1024*1024))

def exportAsJson(result):
	filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json"
	with open(filename,"w+",encoding="utf-8") as f:
		f.writelines(json.dumps(result,sort_keys=True,indent=4,separators=(',',':')))
		f.close()
	print("Result exported as %s" % filename)


