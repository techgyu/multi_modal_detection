# 필요한 패키지: pygetwindow, directkeys.py (SendInput)
# 설치: pip install pygetwindow

import time
import pygetwindow as gw
from directkeys import PressKey, ReleaseKey

def send_n_key_to_arma3():
    # 'Arma 3' 창 찾기
    windows = gw.getWindowsWithTitle('Arma 3')
    if not windows:
        print('Arma 3 실행 창을 찾을 수 없습니다.')
        return False
    win = windows[0]
    if win.isMinimized:
        win.restore()
        time.sleep(0.5)
    win.activate()
    time.sleep(0.5)

    # N키의 가상키코드: 0x4E
    VK_N_SCAN = 0x31  # 'N'의 스캔코드
    PressKey(VK_N_SCAN)
    time.sleep(0.05)
    ReleaseKey(VK_N_SCAN)
    print("[SendInput] 'N' 키를 Arma3 창에 전송했습니다.")
    return True

if __name__ == '__main__':
    send_n_key_to_arma3()

