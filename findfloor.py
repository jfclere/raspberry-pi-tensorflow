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
    print(abs(med[0]-m[0]), abs(med[1]-m[1]), abs(med[2]-m[2]), gap)
    cmed = abs(med[0]-m[0])
    if cmed > gap:
      return False
    cmed = abs(med[1]-m[1])
    if cmed > gap:
      return False
    cmed = abs(med[2]-m[2])
    if cmed > gap:
      return False
    return True

# Compare the colors
def isSameDelta(med, m, gap):
    mdr = med[0]-med[1]
    mdg = med[1]-med[2]
    mdb = med[2]-med[0]
    dr = m[0]-m[1]
    dg = m[1]-m[2]
    db = m[2]-m[0]
    # print("isSameDelta: ", med , m, gap)
    # print(mdr,dr, mdg,dg, mdb,db)
    # brightness
    b1 = (med[0]+med[1]+med[2])/3.0
    b2 = (m[0]+m[1]+m[2])/3.0
    fb = b1/b2
    
    # print(med)
    # print(m)
    # print(fb)
    # print(mdr,dr, mdg,dg, mdb,db)

    # if fb inferior to 1 there is more brightness
    if fb<1:
      gap = gap / fb
    
    print(mdr-dr, mdg-dg, mdb-db, gap)
    cmed = abs(mdr-dr)
    if cmed > gap:
      return False
    cmed = abs(mdg-dg)
    if cmed > gap:
      return False
    cmed = abs(mdb-db)
    if cmed > gap:
      return False
    return True

# write string the image for debug
def writestring(output, text):
    global counttries
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (100, 3000)
    fontScale = 5
    color = (255, 0, 0)
    thickness = 2
    output = cv2.putText(output, text, org, font, fontScale, color, thickness, cv2.LINE_AA) 
    red = "croped" + str(counttries)
    cv2.imwrite("/tmp/now" + red + ".jpg", output)

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
    # Already too different brightness
    if (mgap > 40.0):
       print("gap! ", mgap)
       writestring(output, "NOTOK: gap!")
       return False
    # calculate what could be the same color...
    gap = 8.0
    print("gap: ", gap)
    if not isSameDelta(mmm, mm, gap):
       writestring(output, "NOTOK: isSameDelta!")
       return False
    if stepw:
       # Here check from right or left (h ia zero!)
       mmmm = valFrontsize(image, output, w, w, stepw*3)
       if not isSameDelta(mmmm, mmm, gap):
          writestring(output, "NOTOK: isSameDelta! " + str(stepw*3))
          return False
       else:
          writestring(output, "OK: isSameDelta! " + str(stepw*3))
          return True
    # Make sure there is nothing in front
    ml = valFrontsize(image, output, w, h+h+h, h+h)
    if not isSameDelta(ml, mmm, gap*2.5):
       print("Front left not OK")
       writestring(output, "NOTOK: Front left not OK!")
       return False
    mr = valFrontsize(image, output, w, h+h+h, -(h+h))
    if not isSameDelta(mr, mmm, gap):
       print("Front right not OK")
       writestring(output, "NOTOK: Front right not OK!")
       return False
    writestring(output, "OK!!!")
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

# capture image
def capture():
    # capture main.
    np_array = picam2.capture_array()
    # convert to cv2 internal format.
    frame = cv2.cvtColor(np_array, cv2.COLOR_BGRA2RGB) 
    cv2.imwrite("/tmp/now.jpg", frame)
    return frame

picam2 = Picamera2()

# - Selected unicam format: 4656x3496-pRAA
preview_config = picam2.create_still_configuration(main = {"size": (4656, 3496), "format": "BGR888"})
picam2.configure(preview_config)

picam2.start()
notforwardcount = 0
lastmove=0
while(True):
    #Capture image
    frame = capture() 
    h=256 # move half square up.
    if isFrontOK(frame, h, 0):
      print(counttries, "Space in front!")
      notforwardcount = 0
      lastmove=0
      if not robot.moveforward():
        break
      continue
    # Try to turn Left or Right
    print("Try left!!")
    if isFrontOK(frame, 0, 512):
       print(counttries, "Space on left!")
       if notforwardcount == 2:
         break # We are stuck making right and left...
       notforwardcount = notforwardcount +1
       lastmove=-1
       if not robot.movestatus("Left90"):
         break
       frame = capture() 
       if isFrontOK(frame, h, 0):
         print(counttries, "NEW Space in front!")
         continue
       else:
         # The Left90 is a bad idea turn back to front.
         if not robot.movestatus("Right90"):
           break # We are stuck!
    print("Try right!!")
    if isFrontOK(frame, 0, -512):
       print(counttries, "Space on right!")
       if notforwardcount == 2:
         break # We are stuck!
       notforwardcount = notforwardcount +1
       lastmove=1
       if not robot.movestatus("Right90"):
         break
       frame = capture() 
       if isFrontOK(frame, h, 0):
         print(counttries, "NEW Space in front!")
         continue
       else:
         # The Right90 is a bad idea turn back to front.
         if not robot.movestatus("Left90"):
           continue
         # We probably need to backward...
         print(counttries, "need to backward...")
    break

# When everything done, release the capture
# cap.release()
picam2.close()
