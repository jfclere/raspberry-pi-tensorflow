import cv2 
import numpy as np 
from picamera2 import Picamera2

import robot

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

def oldisFrontOK(image):

    # Get a piece of the floor 3496, 4656
    #h=96
    #w=48
    w=256
    h=int(w*2)
    y=3496 - h
    x=2328 - w # the middle is 2328
    w=int(w*2)

    crop_img = image[y:y+h, x:x+w]
    red = "crop"
    cv2.imwrite("/tmp/now" + red + ".jpg", crop_img)
    med = getMedianImageChannels(crop_img)
    print(med)

    red = "croped"
    output = image.copy()
    cv2.rectangle(output, (x,y),(x+h, y+w),(255,255,255),4)
    cv2.imwrite("/tmp/now" + red + ".jpg", output)

    # We have a medium value for the front which is the floor
    w, h , _ = image.shape
    # cut the big image in pieces and check each piece
    width=16
    height=16
    gap=15
    mmed = med
    mp = med
    output = image.copy()
    # from right to left and top to bottom
    # First reduce the number of colors
    for shape in ([16,16, 30], [32,32, 20], [64, 64, 10]):
    #for shape in ([16,16],):
       width = shape[0]
       height = shape[1]
       gap = shape[2] 
   
       for r in range(0,w,width):
         med = mmed
         for c in range(0,h,height):
             cur_img = image[r:r+width, c:c+height,:]
             m = getMedianImageChannels(cur_img)
             if isSameMedian(med, m, gap):
                 if not isSameMedian(mmed, m, 5*gap):
                    cv2.rectangle(output, (c,r),(c+height, r+width),(0,0,0),-1) # Fill with black
             else:
                 cv2.rectangle(output, (c,r),(c+height, r+width),(0,0,0),-1) # Fill with black
                 med = m

       for c in range(0,h,height):
         med = mmed
         for r in range(0,w,width):
             cur_img = image[r:r+width, c:c+height,:]
             m = getMedianImageChannels(cur_img)
             if isSameMedian(med, m, gap):
                 if not isSameMedian(mmed, m, 5*gap):
                    cv2.rectangle(output, (c,r),(c+height, r+width),(0,0,0),-1) # Fill with black
             else:
                 cv2.rectangle(output, (c,r),(c+height, r+width),(0,0,0),-1) # Fill with black
                 med = m
       # check if we have a black line in front
       infront = False
       for r in range(w-width,int(w/2),-width):
         count = 0
         n = 0;
         for c in range(0,h,height):
             cur_img = output[r:r+width, c:c+height,:]
             if not n:
                 cv2.rectangle(output, (c,r),(c+height, r+width),(255,255,255),-1) # White
             n = n + 1
             m = getMedianImageChannels(cur_img)
             if isSameMedian([0,0,0], m, 0):
               count = count + 1
         if count == int(w/(width*2)):
            infront = True
            break
       if infront:
          cv2.imwrite("/tmp/now1.jpg", output)
          return True
    cv2.imwrite("/tmp/now1.jpg", output)
    return False

def isFrontOK(image, h, stepw):
    output = image.copy()
    w=256
    m = valFrontsize(image, output, w, 0, 0)
    mm = valFrontsize(image, output, w, h, stepw)
    h=h+h
    mmm = valFrontsize(image, output, w, h, stepw+stepw)
    g1 = abs(m[0]-mm[0])
    g1 = abs(m[0]-mm[0])
    g2 = abs(m[1]-mm[1])
    g3 = abs(m[2]-mm[2])
    gap = max(g1, g2)
    gap = max(gap,g3)
    # Already too different
    if (gap > 40.0):
      print("gap! ", gap)
      return False
    gap = gap*2
    print("gap: ", gap)
    if isSameMedian(mmm, mm, gap):
       return True
    return False

# get a square and return value
def valFrontsize(image, output, w, starth, startw):

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

    red = "croped"
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
      break
      # robot.moveforward()
    else:
      print("Try left!!")
      if isFrontOK(frame, 0, 512):
         print("Space on left!")
      print("Try right!!")
      if isFrontOK(frame, 0, -512):
         print("Space on right!")
      break
      #robot.turnright()

# When everything done, release the capture
# cap.release()
picam2.close()
