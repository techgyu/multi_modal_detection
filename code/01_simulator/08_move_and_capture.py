# Arma3 실행 중인 윈도우 화면을 캡처하여 저장하는 코드
# 필요한 패키지: pygetwindow, pyautogui, pillow
# 설치: pip install pygetwindow pyautogui pillow

import os
import pygetwindow as gw
import mss
import numpy as np
from PIL import Image
import time
import win32gui
import win32con
from directkeys import PressKey, ReleaseKey

def capture_arma3_window(win, save_path='data/capture/01_capture_arma3.png'):
	# win: pygetwindow 윈도우 객체 (이미 찾은 창)
	if win.isMinimized:
		print("최소화된 창 복원 중...")
		win.restore()
		time.sleep(0.1)
	win.activate()
	# win32gui로 클라이언트 영역 좌표 얻기
	hwnd = win._hWnd
	rect = win32gui.GetClientRect(hwnd)
	left_top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
	right_bottom = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
	left, top = left_top
	right, bottom = right_bottom
	width = right - left
	height = bottom - top
	# mss로 빠른 캡처
	with mss.mss() as sct:
		monitor = {"left": left, "top": top, "width": width, "height": height}
		img = sct.grab(monitor)
		img_pil = Image.frombytes("RGB", img.size, img.rgb)
		img_pil.save(save_path)
	return True

def send_n_key_to_arma3(win):
	# win: pygetwindow 윈도우 객체 (이미 찾은 창)
	if win.isMinimized:
		win.restore()
	win.activate()
	VK_N_SCAN = 0x31  # 'N'의 스캔코드
	PressKey(VK_N_SCAN)
	ReleaseKey(VK_N_SCAN)
	return True

def main():
	MODES = ['v', 'nv', 'th', 'grid']
	MODE_DIRS = {
		'v': 'E:/data/dataset/visual',
		'nv': 'E:/data/dataset/nvg',
		'th': 'E:/data/dataset/thermal',
		'grid': 'E:/data/dataset/grid',
	}
	time.sleep(5) 
	# 최초 1회만 창 찾기
	windows = gw.getWindowsWithTitle('Arma 3')
	if not windows:
		print('Arma 3 실행 창을 찾을 수 없습니다.')
		return
	win = windows[0]
	if win.isMinimized:
		win.restore()
	win.activate()
	idx = 1
	while True:
		# 1초간 W키(전진) 입력
		VK_W_SCAN = 0x11  # W키 스캔코드
		PressKey(VK_W_SCAN)
		time.sleep(1)
		ReleaseKey(VK_W_SCAN)

		# 이동 전 Shift+V(시점 전환) 입력
		VK_SHIFT_SCAN = 0x2A  # Shift 스캔코드w
		VK_V_SCAN = 0x2F      # V 스캔코드
		PressKey(VK_SHIFT_SCAN)
		PressKey(VK_V_SCAN)
		time.sleep(0.1)
		ReleaseKey(VK_V_SCAN)
		ReleaseKey(VK_SHIFT_SCAN)
		time.sleep(5)

		# 1초간 W키(전진) 입력
		VK_W_SCAN = 0x11  # W키 스캔코드
		PressKey(VK_W_SCAN)
		time.sleep(1)
		ReleaseKey(VK_W_SCAN)

		# 3-way 캡처 및 화면 전환
		for mode in MODES:
			dir_path = MODE_DIRS[mode]
			save_path = os.path.join(dir_path, f"{idx:06d}_{mode}.png")
			if mode == 'grid':
				# ']'키 1회 전송 후 캡처
				VK_RBRACKET_SCAN = 0x1B  # ']'의 스캔코드
				PressKey(VK_RBRACKET_SCAN)
				ReleaseKey(VK_RBRACKET_SCAN)
				time.sleep(2)
				capture_arma3_window(win, save_path)
				# ']'키 2회 전송
				for _ in range(2):
					PressKey(VK_RBRACKET_SCAN)
					ReleaseKey(VK_RBRACKET_SCAN)
					time.sleep(1)
			else:
				capture_arma3_window(win, save_path) # 화면 캡처
				print("capture")
				send_n_key_to_arma3(win) # 화면 전환
				print("change vision")
				time.sleep(2)  # 화면 전환 대기 시간: 2s
		idx += 1

if __name__ == '__main__':
	main()