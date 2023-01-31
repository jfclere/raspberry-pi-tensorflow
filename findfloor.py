import cv2 
import numpy as np 
from picamera2 import Picamera2

import robot
counttries=0

def getMedianImageChannels(im):
    b, g, r = cv2.split(im) # Split channels
    # Remove zeros
    b = b[b != 0]
    g = g[g != 0]
    r = r[r != 0]
    # median values
    b_median = np.median(b)
    r_median = np.median(r)
    g_median = np.median(g)
    return r_median,g_median,b_median

def getMask(img, med, gap):
    rm = med[0]
    gm = med[1]
    bm = med[2]
    rm = rm - gap
    if rm<0:
      rm = 0
    gm = gm - gap
    if gm<0:
      gm = 0
    bm = bm - gap
    if bm<0:
      bm = 0
    lower = np.array([rm, gm, bm], dtype = "uint8") 
    rm = med[0]
    gm = med[1]
    bm = med[2]
    rm = rm + gap
    if rm>255:
      rm = 255
    gm = gm + gap
    if gm>255:
      gm = 255
    bm = bm + gap
    if bm>255:
      bm = 255

    upper= np.array([rm, gm, bm], dtype = "uint8")

    mask = cv2.inRange(img, lower, upper)

    return mask

def isSameMedian(med, m, gap):
    cmed = med[0]
    cm = m[0]
    if cmed < cm-gap or cmed > cm+gap:
      return False
    cmed = med[1]
    cm = m[1]
    if cmed < cm-gap or cmed > cm+gap:
      return False
    cmed = med[2]
    cm = m[2]
    if cmed < cm-gap or cmed > cm+gap:
      return False
    return True

# h the vertical gap and stepw the horizontal one
def isFrontOK(image, h, stepw):
    global counttries
    counttries = counttries + 1
    output = image.copy()
    w=256
    m = valFrontsize(image, output, w, 0, 0)
    mm = valFrontsize(image, output, w, h, stepw)
    mmm = valFrontsize(image, output, w, h+h, stepw+stepw)
    g1 = abs(m[0]-mm[0])
    g1 = abs(m[0]-mm[0])
    g2 = abs(m[1]-mm[1])
    g3 = abs(m[2]-mm[2])
    mgap = max(g1, g2)
    mgap = max(mgap,g3)
    # Already too different
    if (mgap > 40.0):
      print("gap! ", gap)
      return False
    gap = mgap*2
    print("gap: ", gap)
    if not isSameMedian(mmm, mm, gap):
       return False
    if stepw:
       # Here check from right or left (h ia zero!)
       mmmm = valFrontsize(image, output, w, w, stepw*3)
       if not isSameMedian(mmmm, mmm, mgap*4):
          return False
    # Make sure there is nothing in front
    ml = valFrontsize(image, output, w, h+h+h, h+h)
    if not isSameMedian(ml, mm, gap):
       print("Front lelf not OK")
       return False
    mr = valFrontsize(image, output, w, h+h+h, -(h+h))
    if not isSameMedian(mr, mm, gap):
       print("Front right not OK")
       return False
    return True

# get a square and return value
def valFrontsize(image, output, w, starth, startw):

    global counttries
    # Get a piece of the floor 3496, 4656
    h=int(w*2)
    y=(3496 - h) - starth
    x=(2328 - w) - startw # the middle is 2328
    w=int(w*2)

    crop_img = image[y:y+h, x:x+w]
    red = "crop"
    cv2.imwrite("/tmp/now" + red + ".jpg", crop_img)
    med = getMedianImageChannels(crop_img)
    print(med)

    red = "croped" + str(counttries)
    cv2.rectangle(output, (x,y),(x+h, y+w),(255,255,255),4)
    cv2.imwrite("/tmp/now" + red + ".jpg", output)
    return med

picam2 = Picamera2()

# - Selected unicam format: 4656x3496-pRAA
preview_config = picam2.create_still_configuration(main = {"size": (4656, 3496), "format": "BGR888"})
picam2.configure(preview_config)

picam2.start()
while(True):
    #Capture frame-by-frame
    #ret, frame = cap.read()
    # capture main.
    np_array = picam2.capture_array()
    # convert to cv2 internal format.
    frame = cv2.cvtColor(np_array, cv2.COLOR_BGRA2RGB) 
    cv2.imwrite("/tmp/now.jpg", frame)
    h=256 # move half square up.
    startw=0
    if isFrontOK(frame, h, startw):
      print("Space in front!")
      robot.moveforward()
    else:
      print("Try left!!")
      if isFrontOK(frame, 0, 512):
         print("Space on left!")
         robot.turnleft()
         continue
      print("Try right!!")
      if isFrontOK(frame, 0, -512):
         print("Space on right!")
         robot.turnright()
         continue
      break

# When everything done, release the capture
# cap.release()
picam2.close()
