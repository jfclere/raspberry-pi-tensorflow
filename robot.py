#!/usr/bin/python
import pycurl
import cv2
from io import BytesIO
from detect import Detector

def findkibble(mydetector):
  width = 512
  height = 512
  input = mydetector.capture()
  print(input.shape)
  w, h , _ = input.shape
  # First try the whole picture
  found, left, right , top, bottom = mydetector.detect(width, height, input)
  if not found:
    found, left, right , top, bottom = mydetector.finedetect(input)
  if found:
    print(left, right , top, bottom, w , h)
    if left < w/2:
      print("kibble detected on the Left")
      return True, True
    else:
      print("kibble detected on the Right")
      return True, False
  return False, False

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
  print(body.decode('iso-8859-1'))

def turnleft():
  move('Left')

def turnright():
  move('Right')

def moveforward():
  move('Forward')

def movebackward():
  move('Backward')


# move try and turn left or right
def tryturn(n, left, detector):
  i = 0
  while i < n:
    found, loc = findkibble(detector)
    if found:
      return True, loc
    # Not found try to turn left/right
    if left:
      turnleft()
    else:
      turnright()
    i = i + 1
  return False, False
     

def main():

  mydetector = Detector()
  # Try on left
  found, loc = tryturn(5, True, mydetector)
  if not found:
    found , loc = tryturn(10, False, mydetector)

  if found:
    if loc:
      print("On the left!!!")
    else:
      print("On the right!!!")

  # try again....
  found, left = findkibble(mydetector)
  if found:
    if left:
      print("kibble detected on the Left!")
      turnleft()
    else:
      print("kibble detected on the Right!")
      turnright()
    moveforward()
  else:
    print("Ooops no kibble detected!")
    #movebackward()
  mydetector.cleanup()

if __name__ == '__main__':
  main()

