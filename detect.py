import tensorflow_hub as hub
import cv2
import numpy
import tensorflow as tf
import pandas as pd
import math
from picamera2 import Picamera2

class Detector:

  def __init__(self): 

        # Carregar modelos
        #detector = hub.load("https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1")
        # detector = hub.load("efficientdet_lite2_detection_1")
        #detector = hub.load("/home/jfclere/TMP/tensorflow/inference_graph/saved_model/")
        self.detector = hub.load("saved_model/")

        self.usepicam2 = bool(False)
        if not self.usepicam2:
           print("Not self.usepicam2")
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
           print("Can't receive frame (stream end?).")
           self.cap.release()
           self.picam2 = Picamera2()
           preview_config = self.picam2.create_still_configuration(main = {"size": (4656, 3496), "format": "BGR888"})
           self.picam2.configure(preview_config)
           self.picam2.start()
           self.usepicam2 = bool(True)

  def capture(self):
    #Capture frame-by-frame
    if self.usepicam2:
        frame = self.picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
    else:
        ret, frame = self.cap.read()
        rgb = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
    return rgb
    
   
  def detect(self, width, height, frame): 

    #Resize to respect the input_shape
    rgb = cv2.resize(frame, (width , height ))

    #Convert img to RGB
    # rgb = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)

    #Is optional but i recommend (float convertion and convert img to tensor image)
    rgb_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)
    rgb_tensor0 = tf.identity(rgb_tensor)

    #Add dims to rgb_tensor
    rgb_tensor = tf.expand_dims(rgb_tensor , 0)
    
    #boxes, scores, classes, num_detections = detector(rgb_tensor)
    detected = self.detector(rgb_tensor)
    # DEBUG print(detected)
    num = int(detected['num_detections'][0])
    # DEBUG print(num)
    
    real_num_detection = tf.cast(detected['num_detections'][0], tf.int32)
    # DEBUG print(real_num_detection)
    # DEBUG print("after real_num_detection")
    # DEBUG print("after real_num_detection")
    # DEBUG print("after real_num_detection")
    detection_classes = detected['detection_classes'][0]
    #detection_classes = tf.cast(detected['detection_classes'][0], tf.int32)
    detection0 = detection_classes[0]
    # DEBUG print(detection_classes)
    #detection_classes = detected['detection_classes'][0].astype(np.uint8)
    detection_boxes = detected['detection_boxes'][0]
    detection_boxe0 = detection_boxes[0]
    # DEBUG print("detection_boxes")
    # DEBUG print(detection_boxes)
    # DEBUG print("detection_boxes end")
    boxe0 = detection_boxe0.numpy()
    detection_scores =  detected['detection_scores'][0]
    #print(detection_classes)
    #print(detection_boxes)
    # DEBUG print(detection_scores)
    score0 = detection_scores[0]
    # DEBUG print(score0)
    # DEBUG print(score0.numpy())
    # result = tf.math.greater(score0, x)
    # DEBUG print(result)
    # DEBUG print(result.numpy())
    if (score0.numpy() < 0.9):
        # DEBUG print("Not found!")
        return False, 0, 0 , 0, 0 # , cv2.imencode('.jpg', rgb)[1].tobytes()
    else:
        print("Found! ", score0.numpy(), " ", detection0)
        # print(boxe0)
        # print('rgb.shape')
        # print(rgb.shape)
        h, w , _ = frame.shape
        # Something like [0.4156833  0.55372864 0.51923627 0.6624511 ]
        #left = boxe0[0] * w
        #right = boxe0[1] * w
        #top = boxe0[2] * h
        #bottom = boxe0[3] * h 
        top = boxe0[0] * h
        left = boxe0[1] * w
        bottom = boxe0[2] * w
        right = boxe0[3] * h 
        
        left = math.floor(left)
        top = math.floor(top)
        right = math.floor(right)
        bottom = math.floor(bottom)
        print("detect() left: " , left, "top: ", top, "right: ", right, "bottom: ", bottom)
        # TRY O cv2.rectangle(rgb, (left,top),(right,bottom),(255,0,0),5)
        # TRY O cv2.imwrite("/home/jfclere/TMP/now.jpg", rgb)
        # TRY O newimage = tf.io.encode_jpeg(
        # TRY O         rgb_tensor0,
        # TRY O         format='',
        # TRY O         quality=95,
        # TRY O         progressive=False,
        # TRY O         optimize_size=False,
        # TRY O         chroma_downsampling=True,
        # TRY O         density_unit='in',
        # TRY O         x_density=300,
        # TRY O         y_density=300,
        # TRY O         xmp_metadata='',
        # TRY O         name=None)

        # TRY O tf.io.write_file("/tmp/now.jpg", newimage)
        # TRY O newimage = cv2.imread('/tmp/now.jpg')
        # TRY O h, w , _ = newimage.shape
        # TRY O # Something like [0.4156833  0.55372864 0.51923627 0.6624511 ]
        # TRY O right = boxe0[0] * w
        # TRY O left = boxe0[1] * w
        # TRY O bottom = boxe0[2] * h
        # TRY O top = boxe0[3] * h
        # TRY O left = math.floor(left)
        # TRY O top = math.floor(top)
        # TRY O right = math.floor(right)
        # TRY O bottom = math.floor(bottom)
        # TRY O print(left)
        # TRY O print(top)
        # TRY O print(right)
        # TRY O print(bottom)
        # TRY O #cv2.rectangle(newimage, (left,top),(right,bottom),(255,0,0),5)
        # TRY O # draw a small box on each point
        # TRY O cv2.rectangle(newimage, (left,top),(left+2,top+2),(255,0,0),5) # blue
        # TRY O cv2.rectangle(newimage, (right,bottom),(right+2,bottom+2),(0,255,0),5) # green
        # From some reasons the red square seems to be center of the object weird?
        # TRY O cv2.rectangle(newimage, (left,bottom),(left+2,bottom+2),(0,0,255),5) # red
        # TRY O cv2.rectangle(newimage, (right,top),(right+2,top+2),(255,255,255),5) # white
        # TRY O cv2.imwrite("/home/jfclere/TMP/now.jpg", newimage)
        return True, left, right , top, bottom # , cv2.imencode('.jpg', newimage)[1].tobytes()

  def cleanup(self): 
    # When everything done, release the capture
    if self.usepicam2:
        self.picam2.close()
    else:
        self.cap.release()

  # here we cut the image in squares and make the squares smaller and smaller (to 512x512)
  def finedetect(self, input): 
    output = input.copy()
    for cur_shape in ([1536, 1536],[1024, 1024],[512,512]):
      # print(cur_shape[0], cur_shape[1])
      width = cur_shape[0]
      height = cur_shape[1]
      w, h , _ = input.shape
      # cut the big image in pieces and check each piece
      for r in range(0,w,width):
        for c in range(0,h,height):
            # print(c, r, h , w)
            cur_img = input[r:r+width, c:c+height,:]
            # skip small sub images
            curw, curh, _ = cur_img.shape
            if ((curw<50) or (curw<50)):
              print("Too small to find!")
              found = False
            else:
              found, left, right , top, bottom = self.detect(512, 512, cur_img)
            if found:
                left = c + left
                right = c + right
                bottom = r + bottom
                top = r + top
                cv2.rectangle(output, (left,top),(left+10,top+10),(255,9,0),5) # red
                cv2.rectangle(output, (left,bottom),(left+10,bottom+10),(0,255,0),5) # green
                cv2.rectangle(output, (right,top),(right+10,top+10),(0,0,255),5) # blue
                cv2.rectangle(output, (right,bottom),(right+10,bottom+10),(255,0,255),5) # weird color purple
                cv2.rectangle(output, (c,r),(c+height, r+width),(255,255,255),5) # white
                cv2.imwrite("/tmp/now.jpg", output)
                return found, left, right , top, bottom
            else:
                cv2.rectangle(output, (c,r),(c+height, r+width),(255,0,0),5) # blue
            # DEBUG cv2.imwrite(f"/tmp/img{r}_{c}.png",cur_img)

    cv2.imwrite("/tmp/now.jpg", output)
    return False, 0, 0 , 0, 0
  

if __name__=='__main__':    
  mydetector = Detector()
  input = mydetector.capture()
  found, left, right , top, bottom = mydetector.finedetect(input)
  cv2.rectangle(input, (left,top),(left+10,top+10),(255,9,0),5) # red
  cv2.rectangle(input, (left,bottom),(left+10,bottom+10),(0,255,0),5) # green
  cv2.rectangle(input, (right,top),(right+10,top+10),(0,0,255),5) # blue
  cv2.rectangle(input, (right,bottom),(right+10,bottom+10),(255,0,255),5) # weird color purple
  cv2.imwrite("/tmp/now1.jpg", input)
  mydetector.cleanup()
