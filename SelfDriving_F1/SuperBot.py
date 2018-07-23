# -*- coding: utf-8 -*-

import json
import os
import time

import psutil
import pyautogui

import keyboard #Using module keyboard

import random
import sys
from threading import Thread

import numpy as np
from PIL import ImageGrab

from pytesseract import image_to_string
import cv2

from directkeys import PressKey, ReleaseKey, Z, Q, S, D, R, A, E, ESC

CH2_url = 'steam://rungameid/515220'

PROCNAME = "F1_2017.exe"
start_state = "HELLO"
play_state = "PLAYING"
play_timer_max = 60 * 3

state = start_state
takeScrenshot = False

timer = 0.0


def getConfig():
    with open('config.json', encoding='UTF-8') as data_file:
        data = json.load(data_file)
    return data

def getpixel(x, y, newshot):
    #print('New Screen')

    return pyautogui.screenshot().getpixel((x, y))
    # else:
    #     try:
    #         #print('Old Screen')
    #         return screen.getpixel((x, y))
    #     except NameError:
    #         #print('New Screen')
    #         return pyautogui.screenshot().getpixel((x, y))




def pixelMatchesColor(x, y, expectedRGBColor, tolerance=0, newshot=True):
    pix = getpixel(x,y, newshot)
    if len(pix) == 3 or len(expectedRGBColor) == 3:  # RGB mode
        r, g, b = pix[:3]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
    elif len(pix) == 4 and len(expectedRGBColor) == 4:  # RGBA mode
        r, g, b, a = pix
        exR, exG, exB, exA = expectedRGBColor
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance) and (
            abs(a - exA) <= tolerance)
    else:
        assert False, 'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s' % (
            len(pix), len(expectedRGBColor))


def printScreen(message):
    if takeScrenshot:
        if not os.path.exists(debug_directory):
            os.makedirs(debug_directory)
        pyautogui.screenshot('{}/{}{}.png'.format(debug_directory, time.strftime("%m.%d %H.%M.%S", time.gmtime()), message))


def changeState(value):
    global state, timer
    state = value
    timer = 0


def killGame():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == PROCNAME:
            proc.kill()

def matchesButton(position):
    if pixelMatchesColor(position[0], position[1], white_button,
                      tolerance=color_tolerance,newshot=False) or pixelMatchesColor(position[0],
                                                                      position[1],
                                                                      gray_button,
                                                                      tolerance=color_tolerance,newshot=False) \
    or pixelMatchesColor(position[0],
                         position[1],
                         super_white_button,
                         tolerance=color_tolerance,newshot=False) or pixelMatchesColor(
        position[0], position[1], energy_jar_color, tolerance=color_tolerance,newshot=False):
        return True
    return False

def isGameRunning():
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == PROCNAME:
            return True
        else:
            return False

def checkTimer():
    global state
    if state == loading_state and timer > loading_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)
    elif state == matching_state and timer > matching_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)
    elif state == play_state and timer > play_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)
    elif state == gameloading_state and timer > gameloading_timer_max:
        printScreen('Timeout')
        print('Timeout. Restarting the game')
        changeState(start_state)


config = getConfig()

# Menu
print('By using this software you agree with license! You can find it in code.')

takeScrenshot = False

# Position init
# line_pause = (config['line_pause']['x'], config['line_pause']['y'])
# rupteur_top = (config['rupteur_top']['x'], config['rupteur_top']['y'])
# rupteur_dot = (config['rupteur_dot']['x'], config['rupteur_dot']['y'])
# need_downshift = (config['need_downshift']['x'], config['need_downshift']['y'])
# need_upshift = (config['need_upshift']['x'], config['need_upshift']['y'])


# Reading timings
gear_passed = config["timers"]["gear_passed"]
start_delay = config["timers"]["start_delay"]
animation_delay = config["timers"]["animation_delay"]



# Colors
def getColor(config, name):
    return (config["colors"][name]["r"], config["colors"][name]["g"], config["colors"][name]["b"])

color_tolerance = config["color_tolerance"]
white_color = getColor(config, "white_color")
super_white_button = getColor(config, "super_white_button")
red_rupteur_color = getColor(config, "red_rupteur_color")
red_pause_color = getColor(config, "red_pause_color")
red_color_shift_help = getColor(config, "red_color_shift_help")


def CheckIfPause():
    #print('CheckIfPause')
    if pixelMatchesColor(line_pause[0], line_pause[1], red_pause_color, tolerance=color_tolerance,newshot=True):
        print('Jeu actuellement en pause')
        time.sleep(animation_delay)
        # PressKey(ESC)

def RunCheck():
    screen = pyautogui.screenshot()
    number = 0
    for check in config['checks']:
        x = check['x']
        y = check['y']
        compare_color = getColor(config, check['color'])
        if check['key_press'] == "UPSHIFT":
            key_press = E
        elif check['key_press'] == "DOWNSHIFT":
            key_press = A
        elif check['key_press'] == "ESC":
            key_press = Z
        elif check['key_press'] == "DRS_BUTTON":
            key_press = R
        else:
            key_press = ESC
        pix = screen.getpixel((x, y))
        # print('{}. {} x:{} y:{} color:{}'.format(number, check['name'], x, y, compare_color))
        if len(pix) == 3 or len(compare_color) == 3:  # RGB mode
            r, g, b = pix[:3]
            exR, exG, exB = compare_color[:3]
            if (abs(r - exR) <= color_tolerance) and (abs(g - exG) <= color_tolerance) and (abs(b - exB) <= color_tolerance):
                # print('true')
                PressKey(key_press)
                time.sleep(0.05)
                ReleaseKey(key_press)
                number += 1
            else:
                number += 1
        elif len(pix) == 4 and len(compare_color) == 4:  # RGBA mode
            r, g, b, a = pix
            exR, exG, exB, exA = compare_color
            if (abs(r - exR) <= color_tolerance) and (abs(g - exG) <= color_tolerance) and (abs(b - exB) <= color_tolerance) and (abs(a - exA) <= color_tolerance):
                # print('true')
                PressKey(key_press)
                time.sleep(0.05)
                ReleaseKey(key_press)
                number += 1
            else:
                number += 1

        else:
            assert False, 'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s' % (
                len(pix), len(compare_color))


# Game info
while (1):
    if state == start_state:
        try:
            already_lauch = False
            for proc in psutil.process_iter():
                if proc.name() == PROCNAME:
                    already_lauch = True
            if already_lauch:
                print("F1 2017 already launched")
                changeState(play_state)
            else:
                print("F1 2017 need to be launched")
                time.sleep(start_delay)
                changeState(start_state)
        except Exception as ex:
            print('Something went wrong while starting F1 2017... Error message: {}'.format(ex))
    elif state == play_state:
        # CheckIfPause()
        RunCheck()
