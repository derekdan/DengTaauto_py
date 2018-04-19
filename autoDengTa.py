#! /usr/bin/env python
#coding=utf-8
import cv2
import numpy as np
import requests
import json
import sys
import os
from pymouse import PyMouse
from PIL import Image, ImageGrab
import time
import aircv as ac
import logging
#from pykeyboard import PyKeyboard

logging.basicConfig(level = logging.INFO,
		format = '%(levelname)s %(message)s')

CONFIDENCE = 0.8  #相似度系数
sc_path = 'C:/autojump.jpg'
ansarray = []
'''
用于截图当前屏幕
'''
def get_screenshot():
    x_dim, y_dim = m.screen_size()
    img_rgb = ImageGrab.grab((0,0,x_dim,y_dim-40))
    img_rgb.save(sc_path)

m = PyMouse()
#k = PyKeyboard()

def get_answer():
	url = 'http://xxjs.dtdjzx.gov.cn/quiz-api/game_info/lookBackSubject'
	roundOnlyId = raw_input(unicode('输入roundOnlyId: ','utf-8').encode('gbk'))
	data = {
		'roundOnlyId':roundOnlyId
	}
	r= requests.post(url,data=data)
	res = json.loads(r.text)
	for tmpData in res['data']['dateList']:
		ansarray.append(tmpData['answer'])	

'''
依次答题
'''
def loop_answer():
	for index,ans in enumerate(ansarray):
		get_screenshot()
		imsrc = ac.imread(sc_path)
		print u"第%d题答案：%s" %(index+1, ans)
		final_ans = ans.split(',')
		for answer in final_ans:
			imres = ac.imread('C:/%s.jpg' % answer)
			pos = ac.find_template(imsrc,imres)
			if pos is not None:
				logging.debug(u'%s.jpg相似度%f' %(answer, pos['confidence']))
				if pos['confidence'] > CONFIDENCE:
					m.press(pos['result'][0],pos['result'][1])
			else:
				logging.error(u'无法定位到答案')
		time.sleep(1)			

		if(index < len(ansarray) - 1):
			imnext = ac.imread('C:/next.jpg')
			nextpos = ac.find_template(imsrc,imnext)
			if nextpos is not None:
				logging.debug(u'next.jpg相似度%f' %(pos['confidence']))
				if nextpos['confidence'] > CONFIDENCE:
					m.press(nextpos['result'][0],nextpos['result'][1])
			else:
				logging.error(u'无法定位到下一个按钮')
			time.sleep(1)		
'''
提交
'''
def submit_answer():
	#点击交卷
	get_screenshot()
	imsrc = ac.imread(sc_path)
	imsubmit = ac.imread('C:/submit.jpg')
	submitpos = ac.find_template(imsrc,imsubmit)
	if submitpos is not None:
		logging.debug(u'交卷按钮相似度%f' % submitpos['confidence'])
		if(submitpos['confidence'] > CONFIDENCE):
			m.press(submitpos['result'][0],submitpos['result'][1])
			print (u'>>交卷')
		else:
			logging.error(u'未找到交卷按钮')
	else:
		logging.error(u'无法定位到交卷按钮')
	time.sleep(2)
	#点击确定
	get_screenshot()
	imsrc = ac.imread(sc_path)
	imyes = ac.imread('C:/yes.jpg')
	yespos = ac.find_template(imsrc,imyes)
	if yespos is not None:
		logging.debug(u'确定按钮相似度%f' % yespos['confidence'])
		if(yespos['confidence'] > CONFIDENCE):
			m.press(yespos['result'][0],yespos['result'][1])
			print (u'>>完成答题')
		else:
			logging.error(u'未找到确定按钮')
	else:
		logging.error(u'无法定位到确定按钮')


if __name__ == '__main__':
	logging.info(u'当前屏幕分辨率为{}'.format(m.screen_size()))
	get_answer()
	print (u'>>>开始答题,请在3秒内将桌面切换为答题界面...')
	time.sleep(3)
	loop_answer()
	submit_answer()