import cv2
import glob
import numpy as np
import time
import os
from selenium import webdriver
from pynput.keyboard import Key, Controller
from PIL import ImageGrab
from win32gui import GetWindowText, GetForegroundWindow

home = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()
sec = time.time()
ducking = time.time()
max_speed = 116
jump_dist = 70
duck_time = 0.1
velocity_coeff = 2.5
match_threshold = 0.8
ptero_height = 110
is_duck = False
global dino_trace_x

dino_traces = []
files = glob.glob(home + '\Object_screenshots\Dino*.jpg')
for file in files:
    temp = cv2.imread(file, 0)
    dino_traces.append(temp)

cactus_traces = []
files = glob.glob(home + '\Object_screenshots\Cactus*.jpg')
for file in files:
    temp = cv2.imread(file, 0)
    cactus_traces.append(temp)

ptero_traces = []
files = glob.glob(home + '\Object_screenshots\Ptero*.jpg')
for file in files:
    temp = cv2.imread(file, 0)
    ptero_traces.append(temp)

keyboard = Controller()
driver = webdriver.Chrome()
driver.set_window_size(240,320)
driver.get("chrome://dino/")
focus = GetWindowText(GetForegroundWindow())
if 'No internet' in driver.page_source:
    keyboard.press(Key.space)

while(True):

    if time.time() - sec >= 1 and time.time() - start_time < max_speed and GetWindowText(GetForegroundWindow()) == focus:
        jump_dist += velocity_coeff
        sec = time.time()

    if time.time() - start_time >= max_speed:
        duck_time = 0.06

    screen = np.array(ImageGrab.grab(bbox=(25,135,490,320)))
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    for dino in dino_traces:
        res_dino = cv2.matchTemplate(screen_gray, dino, cv2.TM_CCOEFF_NORMED)
        loc_dino = np.where(res_dino >= match_threshold)
        w_dino, h_dino = dino.shape[::-1]
        for dino_tr in zip(*loc_dino[::-1]):
            dino_trace_x = dino_tr[0] + w_dino
            if is_duck == True and time.time() - ducking >= duck_time:
                keyboard.release(Key.down)
                is_duck = False

            cv2.rectangle(screen, dino_tr, (dino_tr[0] + w_dino, dino_tr[1] + h_dino), (50,205,50), 1)

    for ptero in ptero_traces:
        res_ptero = cv2.matchTemplate(screen_gray, ptero, cv2.TM_CCOEFF_NORMED)
        w_ptero, h_ptero = ptero.shape[::-1]
        loc_ptero = np.where(res_ptero >= match_threshold)
        for ptero_tr in zip(*loc_ptero[::-1]):
            if ptero_tr[1] in range(ptero_height, ptero_height-20, -1) and dino_trace_x + jump_dist/2 > ptero_tr[0]:
                keyboard.press(Key.down)
                is_duck = True
                ducking = time.time()
            elif ptero_tr[1] > ptero_height and dino_trace_x + jump_dist > ptero_tr[0]:
                keyboard.press(Key.space)

            cv2.rectangle(screen, ptero_tr, (ptero_tr[0] + w_ptero, ptero_tr[1] + h_ptero), (158, 10, 10), 1)

    for cactus in cactus_traces:
        res_cactus = cv2.matchTemplate(screen_gray, cactus, cv2.TM_CCOEFF_NORMED)
        w_cactus, h_cactus = cactus.shape[::-1]
        loc_cactus = np.where(res_cactus >= match_threshold)
        for cactus_tr in zip(*loc_cactus[::-1]):
            if dino_trace_x + jump_dist > cactus_tr[0]:
                keyboard.press(Key.space)

            cv2.rectangle(screen, cactus_tr, (cactus_tr[0] + w_cactus, cactus_tr[1] + h_cactus), (0, 0, 255), 1)

    cv2.moveWindow('image', 16, 330)
    cv2.imshow('image', screen)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
