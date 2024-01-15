#!/usr/bin/python
import requests
import cv2
from io import BytesIO
from detect import Detector
import time

# Find the image and return found, left, right, nearenough
def findkibble(mydetector):
  input = mydetector.capture()
  print(input.shape)
  h, w , _ = input.shape
  # First try the whole picture
  found, left, right , top, bottom = mydetector.detect(512, 512, input)
  if found:
    # trace the first dectection as mydetector.detect doesn't trace via images
    cv2.rectangle(input, (left,top),(left+10,top+10),(255,9,0),5) # red
    cv2.rectangle(input, (left,bottom),(left+10,bottom+10),(0,255,0),5) # green
    cv2.rectangle(input, (right,top),(right+10,top+10),(0,0,255),5) # green
    cv2.rectangle(input, (right,bottom),(right+10,bottom+10),(255,0,255),5) # weird color purple
    cv2.rectangle(input, (0,0),(w,h),(255,0,255),5) # weird color purple
    cv2.imwrite("/tmp/now.jpg", input)
    # For some reason the left and right are inverted... Sometime
    if left>right:
      print("left>right!")
      myleft = left
      left = right
      right = myleft
  if not found:
    found, left, right , top, bottom = mydetector.finedetect(input)
  if found:
    # left, front, right (0,0) is the upper top and (w, h) the right bottom
    print("Found: ", found, "left: ", left, "right: ", right , "top: ", top, "bottom: ", bottom);
    nearenough = False
    size = (right-left) * (bottom-top)
    print(left, right , top, bottom, w , h, size)
    if size < 0:
      # Oops what is wrong...
      raise Exception("size < 0")
    if size > (w*h)/42:
      nearenough = True
    # decide if the object is on the left or the right
    middle = left + (right - left) / 2
    l = (w * 3 )/8
    r = (w * 6 )/8
    if middle < l:
      print("kibble detected on the Left")
      return True, True, False, nearenough
    if middle > r:
      print("kibble detected on the Right")
      return True, False, True, nearenough
    print("kibble detected on the Front")
    return True, False, False, nearenough
  return False, False, False, False

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


# move try and turn left or right
def tryturn(n, goleft, detector, hostname):
  i = 0
  while i < n:
    found, left, right , near = findkibble(detector)
    if found:
      return found, left, right, near
    # Not found try to turn left/right
    if goleft:
      turnleft(hostname)
    else:
      turnright(hostname)
    i = i + 1
  return False, False, False, False

def stepforward(mydetector, hostname):
  # Try on left
  found, left, right, near = tryturn(5, True, mydetector, hostname)
  if not found:
    turnright(hostname)
    time.sleep(1) # Sleep for 1 second
    turnright(hostname)
    time.sleep(1) # Sleep for 1 second
    turnright(hostname)
    time.sleep(1) # Sleep for 1 second
    turnright(hostname)
    time.sleep(1) # Sleep for 1 second
    turnright(hostname)
    time.sleep(1) # Sleep for 1 second
    found, left, right, near = tryturn(5, False, mydetector, hostname)

  if found:
    if left:
      print("On the left!!!")
      turnleft(hostname)
    elif right:
      print("On the right!!!")
      turnright(hostname)
    else:
      print("kibble detected in the Front!")
      moveforward(hostname)
  else:
    print("Ooops no kibble detected!")
    return False, False
  if near:
    print("kibble near!")
    return True, True
  else:
    return True, False

def main():

  hostname = '192.168.1.80'
  mydetector = Detector(hostname)
  f = True
  while f:
    # We stop for 2 reasons not found or near.
    f, n = stepforward(mydetector, hostname)
    if n:
      # near try to finish
      found, left, right, nearenough = findkibble(mydetector)
      if left:
        turnleft(hostname)
      elif right:
        turnleft(hostname)
      elif nearenough:
        moveforward(hostname)
      break
      
  mydetector.cleanup()

if __name__ == '__main__':
  main()

