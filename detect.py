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

   
  def detect(self, width, height): 

    #Capture frame-by-frame
    if self.usepicam2:
        frame = self.picam2.capture_array()
    else:
        ret, frame = self.cap.read()
    
    #Resize to respect the input_shape
    inp = cv2.resize(frame, (width , height ))

    #Convert img to RGB
    rgb = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)

    #Is optional but i recommend (float convertion and convert img to tensor image)
    rgb_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)
    rgb_tensor0 = tf.identity(rgb_tensor)

    #Add dims to rgb_tensor
    rgb_tensor = tf.expand_dims(rgb_tensor , 0)
    
    #boxes, scores, classes, num_detections = detector(rgb_tensor)
    detected = self.detector(rgb_tensor)
    print(detected)
    num = int(detected['num_detections'][0])
    print(num)
    
    real_num_detection = tf.cast(detected['num_detections'][0], tf.int32)
    print(real_num_detection)
    print("after real_num_detection")
    print("after real_num_detection")
    print("after real_num_detection")
    #detection_classes = detected['detection_classes'][0]
    detection_classes = tf.cast(detected['detection_classes'][0], tf.int32)
    print(detection_classes)
    #detection_classes = detected['detection_classes'][0].astype(np.uint8)
    detection_boxes = detected['detection_boxes'][0]
    detection_boxe0 = detection_boxes[0]
    print("detection_boxes")
    print(detection_boxes)
    print("detection_boxes end")
    boxe0 = detection_boxe0.numpy()
    detection_scores =  detected['detection_scores'][0]
    #print(detection_classes)
    #print(detection_boxes)
    print(detection_scores)
    score0 = detection_scores[0]
    print(score0)
    print(score0.numpy())
    x = tf.constant(0.3)
    print(x)
    result = tf.math.greater(score0, x)
    print(result)
    print(result.numpy())
    if (score0.numpy() < 0.9):
        print("Not found!")
        return cv2.imencode('.jpg', rgb)[1].tobytes()
    else:
        print("Found!")
        print(boxe0)
        print('rgb.shape')
        print(rgb.shape)
        h, w , _ = rgb.shape
        # Something like [0.4156833  0.55372864 0.51923627 0.6624511 ]
        left = boxe0[0] * w
        right = boxe0[1] * w
        top = boxe0[2] * h
        bottom = boxe0[3] * h 
        left = math.floor(left)
        top = math.floor(top)
        right = math.floor(right)
        bottom = math.floor(bottom)
        print(left)
        print(top)
        print(right)
        print(bottom)
        cv2.rectangle(rgb, (left,top),(right,bottom),(255,0,0),5)
        cv2.imwrite("/home/jfclere/TMP/now.jpg", rgb)
        newimage = tf.io.encode_jpeg(
                rgb_tensor0,
                format='',
                quality=95,
                progressive=False,
                optimize_size=False,
                chroma_downsampling=True,
                density_unit='in',
                x_density=300,
                y_density=300,
                xmp_metadata='',
                name=None)

        tf.io.write_file("/tmp/now.jpg", newimage)
        newimage = cv2.imread('/tmp/now.jpg')
        h, w , _ = newimage.shape
        # Something like [0.4156833  0.55372864 0.51923627 0.6624511 ]
        right = boxe0[0] * w
        left = boxe0[1] * w
        bottom = boxe0[2] * h
        top = boxe0[3] * h
        left = math.floor(left)
        top = math.floor(top)
        right = math.floor(right)
        bottom = math.floor(bottom)
        print(left)
        print(top)
        print(right)
        print(bottom)
        #cv2.rectangle(newimage, (left,top),(right,bottom),(255,0,0),5)
        # draw a small box on each point
        cv2.rectangle(newimage, (left,top),(left+2,top+2),(255,0,0),5) # blue
        cv2.rectangle(newimage, (right,bottom),(right+2,bottom+2),(0,255,0),5) # green
        # From some reasons the red square seems to be center of the object weird?
        cv2.rectangle(newimage, (left,bottom),(left+2,bottom+2),(0,0,255),5) # red
        cv2.rectangle(newimage, (right,top),(right+2,top+2),(255,255,255),5) # white
        cv2.imwrite("/home/jfclere/TMP/now.jpg", newimage)
        return cv2.imencode('.jpg', newimage)[1].tobytes()

  def cleanup(self): 
    # When everything done, release the capture
    if self.usepicam2:
        self.picam2.close()
    else:
        self.cap.release()

if __name__=='__main__':    
  width = 512
  height = 512
  mydetector = Detector()
  image = mydetector.detect(width, height)
  mydetector.cleanup()
