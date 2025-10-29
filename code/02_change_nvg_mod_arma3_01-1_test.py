# directkeys.py가 제대로 동작하는지 확인용
import time
from directkeys import PressKey, ReleaseKey

VK_N_SCAN = 0x31  # 'N'의 스캔코드
PressKey(VK_N_SCAN)
time.sleep(0.05)
ReleaseKey(VK_N_SCAN)
print("N키 입력 완료")