#!/usr/bin/python
import pycurl
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

def move(direction):
  buffer = BytesIO()
  c = pycurl.Curl()
  c.setopt(c.URL, 'http://192.168.1.119/cgi-bin/'+direction+'.py')
  c.setopt(c.WRITEDATA, buffer)
  #c.setopt(c.CAINFO, certifi.where())
  c.perform()
  c.close()

  body = buffer.getvalue()
  # Body is a byte string.
  # We have to know the encoding in order to print it to a text file
  # such as standard output.
  result = body.decode('iso-8859-1')
  print(result)
  if "Failed:" in result: 
    return False
  # We need to wait until the move is done.
  # time.sleep(1) # Sleep for 1 second
  return True

def movestatus(direction):
  if move(direction):
    time.sleep(0.2)
    if move('Status'):
      return True
  return False

def turnleft():
  return movestatus('Left')

def turnright():
  return movestatus('Right')

def moveforward():
  return movestatus('Forward')

def movebackward():
  return movestatus('Backward')


# move try and turn left or right
def tryturn(n, goleft, detector):
  i = 0
  while i < n:
    found, left, right , near = findkibble(detector)
    if found:
      return found, left, right, near
    # Not found try to turn left/right
    if goleft:
      turnleft()
    else:
      turnright()
    i = i + 1
  return False, False, False, False

def stepforward(mydetector):
  # Try on left
  found, left, right, near = tryturn(5, True, mydetector)
  if not found:
    turnright()
    time.sleep(1) # Sleep for 1 second
    turnright()
    time.sleep(1) # Sleep for 1 second
    turnright()
    time.sleep(1) # Sleep for 1 second
    turnright()
    time.sleep(1) # Sleep for 1 second
    turnright()
    time.sleep(1) # Sleep for 1 second
    found, left, right, near = tryturn(5, False, mydetector)

  if found:
    if left:
      print("On the left!!!")
      turnleft()
    elif right:
      print("On the right!!!")
      turnright()
    else:
      print("kibble detected in the Front!")
      moveforward()
  else:
    print("Ooops no kibble detected!")
    return False, False
  if near:
    print("kibble near!")
    return True, True
  else:
    return True, False

def main():

  mydetector = Detector()
  f = True
  while f:
    # We stop for 2 reasons not found or near.
    f, n = stepforward(mydetector)
    if n:
      # near try to finish
      found, left, right, nearenough = findkibble(mydetector)
      if left:
        turnleft()
      elif right:
        turnleft()
      elif nearenough:
        moveforward()
      break
      
  mydetector.cleanup()

if __name__ == '__main__':
  main()

