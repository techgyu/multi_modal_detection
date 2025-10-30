# Arma3 실행 중인 윈도우 화면을 캡처하여 저장하는 코드
# 필요한 패키지: pygetwindow, pyautogui, pillow
# 설치: pip install pygetwindow pyautogui pillow

import os
import pygetwindow as gw
import pyautogui
from PIL import Image
import time

def capture_arma3_window(save_path='data/capture/01_capture_arma3.png'):
	# 윈도우 타이틀에 'Arma 3'가 포함된 창 찾기
	windows = gw.getWindowsWithTitle('Arma 3')
	if not windows:
		print('Arma 3 실행 창을 찾을 수 없습니다.')
		return False
	win = windows[0]
	# 창이 최소화되어 있으면 복원
	if win.isMinimized:
		win.restore()
		time.sleep(0.5)
	# 창을 맨 앞으로 가져오기
	win.activate()
	time.sleep(0.5)
	# 창 위치 및 크기
	left, top, width, height = win.left, win.top, win.width, win.height
	# 화면 캡처
	screenshot = pyautogui.screenshot(region=(left, top, width, height))
	# 폴더가 없으면 생성
	os.makedirs(os.path.dirname(save_path), exist_ok=True)
	screenshot.save(save_path)
	print(f'Arma3 화면을 {save_path}로 저장했습니다.')
	return True

if __name__ == '__main__':
	capture_arma3_window()
