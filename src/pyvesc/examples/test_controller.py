#!/usr/bin/env python
# coding: utf-8


import pygame
import time
import numpy as np
import traceback

pygame.init()
pygame.joystick.init()

nb_joy = pygame.joystick.get_count()
print("nb joysticks: {}".format(nb_joy))

J = pygame.joystick.Joystick(0)
try :
    while True:
        if nb_joy != pygame.joystick.get_count() :
            print("THIS COUNTS AS A DECONNECTION")
            break
        for event in pygame.event.get():
            pass
        print("x = {}, y = {}, rot={}".format(J.get_axis(0), -J.get_axis(1), -J.get_axis(3)))
        time.sleep(0.1)
except Exception as e:
    traceback.print_exc()
finally :
    J.quit()
