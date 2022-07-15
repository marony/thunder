# -*- coding: utf-8 -*-
from PIL import Image
import cv2
import numpy as np
import random
import time
import sys
import winxpgui
from ctypes import *
import win32gui
import win32ui
import win32con
user32 = windll.user32

# Windowsのシステム設定の拡大率
window_scale = 1.25

VK_RETURN = 0x0D # Enter キー
VK_ESCAPE = 0x1B # ESC キー
VK_LEFT   = 0x25 # 左方向キー
VK_UP     = 0x26 # 上方向キー
VK_RIGHT  = 0x27 # 右方向キー
VK_DOWN   = 0x28 # 下方向キー

# EnumWindowsに渡す関数
# ar: [0] = タイトル, [1] = ウインドウハンドルの配列
def proc(hwnd, ar):
	title = winxpgui.GetWindowText(hwnd)
	if ar[0] in title:
		ar[1].append(hwnd)
	return 1

# タイトルからウインドウハンドルを取得する
# n: 見つかった何番目を返却するか
def getid(title, n = 0):
	hwnds = []
	winxpgui.EnumWindows(proc, [ title, hwnds ])
	return hwnds[n]

# スクリーンショット
# 微妙に大きさずれてるけど大勢に影響ないので無視
def screenshot(hwnd):
	# ウインドウの大きさなど取得
	size = winxpgui.GetClientRect(hwnd)
	#print(size)
	rect = winxpgui.GetWindowRect(hwnd)
	#print(rect)
	# デスクトップ上のウインドウの大きさからウインドウ内部の大きさを引く
	dx = (rect[2] - rect[0]) - (size[2] - size[0])
	dy = (rect[3] - rect[1]) - (size[3] - size[1])
	#print(dx, dy)
	x = int(dx / 2)
	y = int(dy / 2)
	width = int(size[2] * window_scale)
	height = int(size[3] * window_scale)
    # ウインドウのコンテキストを取得
	window_dc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(hwnd))
	compatible_dc = window_dc.CreateCompatibleDC()
    # ウインドウの画像を取得
	bmp = win32ui.CreateBitmap()
	bmp.CreateCompatibleBitmap(window_dc, width, height)
	compatible_dc.SelectObject(bmp)
	compatible_dc.BitBlt((0, 0), (width, height), window_dc, (x, y), win32con.SRCCOPY)
	img = Image.frombuffer('RGB', (width, height), bmp.GetBitmapBits(True), 'raw', 'RGBX', 0, 1)
	# クリーンナップ
	win32gui.DeleteObject(bmp.GetHandle())
	compatible_dc.DeleteDC()
	window_dc.DeleteDC()
	win32gui.ReleaseDC(hwnd, win32gui.GetWindowDC(hwnd)) 

	return img

def keyboard(keycode, t = 0.1):
	user32.keybd_event(keycode, 0, 0, 0)
	time.sleep(t)
    # KEYEVENTF_KEYUP: 0x0002
	user32.keybd_event(keycode, 0, 0x2, 0)

# まいんちゃん
if __name__ == '__main__':
	hwnd = getid("PS Remote Play")
	c = 0
	while True:
		time.sleep(0.01)
		image = screenshot(hwnd)
		# ピクセルの取得
		p1 = image.getpixel((50, 100))
		p2 = image.getpixel((590, 100))
		p3 = image.getpixel((50, 540))
		p4 = image.getpixel((590, 540))
		# RGBの平均が一定を超えたらENTERキーを押す
		a = (p1[0] + p1[1] + p1[2] +
			p2[0] + p2[1] + p2[2] +
			p3[0] + p3[1] + p3[2] +
			p4[0] + p4[1] + p4[2]) / 12
		if a >= 100:
			print(p1, p2, p3, p4)
			# 雷を避ける
			keyboard(VK_RETURN, 0.2)
			c = c + 1
			print(c)
			# 避けてる間のウエイト
			time.sleep(0.8)
			# 少し上に戻る
			keyboard(VK_UP, 1.0)

