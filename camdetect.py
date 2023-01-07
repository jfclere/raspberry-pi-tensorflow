import tensorflow_hub as hub
import cv2
import numpy
import tensorflow as tf
import pandas as pd
from picamera2 import Picamera2

# Carregar modelos
# detector = hub.load("efficientdet_lite2_detection_1")
detector = hub.load("https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1")
labels = pd.read_csv('labels.csv',sep=';',index_col='ID')
labels = labels['OBJECT (2017 REL.)']

from picamera2 import Picamera2

picam2 = Picamera2()

# - Selected unicam format: 4656x3496-pRAA
preview_config = picam2.create_still_configuration(main = {"size": (4656, 3496), "format": "BGR888"})
picam2.configure(preview_config)

picam2.start()
# cap = cv2.VideoCapture(0)

width = 512
height = 512

while(True):
    #Capture frame-by-frame
    #ret, frame = cap.read()
    # capture main.
    np_array = picam2.capture_array()
    # convert to cv2 internal format.
    frame = cv2.cvtColor(np_array, cv2.COLOR_BGRA2RGB) 
    
    #Resize to respect the input_shape
    inp = cv2.resize(frame, (width , height ))

    #Convert img to RGB
    rgb = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)

    #Is optional but i recommend (float convertion and convert img to tensor image)
    rgb_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)

    #Add dims to rgb_tensor
    rgb_tensor = tf.expand_dims(rgb_tensor , 0)
    
    boxes, scores, classes, num_detections = detector(rgb_tensor)
    
    pred_labels = classes.numpy().astype('int')[0]
    
    pred_labels = [labels[i] for i in pred_labels]
    pred_boxes = boxes.numpy()[0].astype('int')
    pred_scores = scores.numpy()[0]
    #loop throughout the faces detected and place a box around it
    
    for score, (ymin,xmin,ymax,xmax), label in zip(pred_scores, pred_boxes, pred_labels):
        if score < 0.5:
            continue
            
        score_txt = f'{100 * round(score,0)}'
        img_boxes = cv2.rectangle(rgb,(xmin, ymax),(xmax, ymin),(0,255,0),1)      
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img_boxes,label,(xmin, ymax-10), font, 0.5, (255,0,0), 1, cv2.LINE_AA)
        cv2.putText(img_boxes,score_txt,(xmax, ymax-10), font, 0.5, (255,0,0), 1, cv2.LINE_AA)



    #Save the resulting frame
    try: img_boxes
    except NameError: img_boxes = None
    if img_boxes is None:
        print("Nothing found!!!")
        cv2.imwrite("/tmp/now.jpg", rgb)
    else:
        cv2.imwrite("/tmp/now.jpg", img_boxes)
        break

# When everything done, release the capture
# cap.release()
picam2.close()
cv2.destroyAllWindows()
