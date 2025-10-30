# Arma3 실행 중인 윈도우 화면을 캡처하여 저장하는 코드
# 필요한 패키지: pygetwindow, pyautogui, pillow
# 설치: pip install pygetwindow pyautogui pillow

import os
import pygetwindow as gw
import pyautogui
from PIL import Image
import time
import win32gui
import win32con
from directkeys import PressKey, ReleaseKey

def capture_arma3_window(win, save_path='data/capture/01_capture_arma3.png'):
	# win: pygetwindow 윈도우 객체 (이미 찾은 창)
	# 창이 최소화되어 있으면 복원
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
	# 화면 캡처 (클라이언트 영역만)
	screenshot = pyautogui.screenshot(region=(left, top, width, height))
	screenshot.save(save_path)
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
	MODES = ['v', 'ir', 'th']
	MODE_DIRS = {
		'v': 'data/dataset/visual',
		'ir': 'data/dataset/ir',
		'th': 'data/dataset/thermal',
	}
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
	mode_idx = 0
	while True:
		mode = MODES[mode_idx]
		dir_path = MODE_DIRS[mode]
		save_path = os.path.join(dir_path, f"{idx:06d}_{mode}.png")
		capture_arma3_window(win, save_path) # 화면 캡처
		# time.sleep(0.1)  # 화면 전환 대기 시간: 0.1s
		send_n_key_to_arma3(win) # 화면 전환
		time.sleep(0.1)  # 캡처 대기 시간: 0.1s
		mode_idx += 1
		if mode_idx == 3:
			mode_idx = 0
			idx += 1
			time.sleep(1)  # 인덱스가 넘어갈 때 1초 대기

if __name__ == '__main__':
	main()