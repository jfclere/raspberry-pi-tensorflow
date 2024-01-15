#!/usr/bin/python3
# finish docking after robot.py
# test charging using gpio=26

import RPi.GPIO as GPIO
import requests
import time

def move(direction, hostname):
  r = requests.get('http://' + hostname + '/cgi-bin/'+direction+'.py')
  result = r.text
  print(result)
  if "Failed:" in result: 
    return False
  # We need to wait until the move is done.
  # time.sleep(1) # Sleep for 1 second
  return True

def movestatus(direction, hostname):
  if move(direction, hostname):
    time.sleep(0.2)
    if move('Status', hostname):
      return True
  return False

def turnleft(hostname):
  return movestatus('Left', hostname)

def turnright(hostname):
  return movestatus('Right', hostname)

def moveforward(hostname):
  return movestatus('Forward', hostname)

def movebackward(hostname):
  return movestatus('Backward', hostname)


CHARGEGPIO=26
hostname = "localhost"

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CHARGEGPIO,GPIO.IN)

i = GPIO.input(CHARGEGPIO)

while i != 1:
  i = GPIO.input(CHARGEGPIO)
  retmove = False
  retforward = moveforward(hostname)
  if not retforward:
    retleft = turnleft(hostname)
    if not retleft:
      retright = turnright(hostname)
  # if all failed we are stuck...
  if retforward or retleft or retright:
    retmove = True 
  if not retmove:
    print("Stuck logic is broken!!!")
    break

print("Docked charging!")
