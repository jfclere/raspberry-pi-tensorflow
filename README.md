# raspberry-pi-tensorflow

This is a repository from the article https://towardsdatascience.com/object-detection-with-tensorflow-model-and-opencv-d839f3e42849

# JFC notes on how to create the model:
(I start with https://github.com/tensorflow/models.git models/research/object_detection/TMP/models/research/object_detection/dockerfiles/tf2/Dockerfile)

## start the pod:
```
podman run -it --rm -p 6006:6006 --user=root -net=host quay.io/jfclere/kibble_tensorflow bash
/home/tensorflow/models/research/object_detection
```

outside:

```
wget http://download.tensorflow.org/models/object_detection/tf2/20200711/efficientdet_d0_coco17_tpu-32.tar.gz

tar -xf efficientdet_d0_coco17_tpu-32.tar.gz

podman cp /home/jfclere/TMP/models/research/object_detection/model_main_tf2.sh 5d3ab326d30b:/home/tensorflow/models/research/object_detection/model_main_tf2.sh
podman cp ./tensorflow/raspberry-pi-tensorflow/TMP/efficientdet_d0_coco17_tpu-32.tar.gz 5d3ab326d30b:/home/tensorflow/models/research/object_detection
podman cp /home/jfclere/TMP/tensorflow/TMP 5d3ab326d30b:/home/jfclere/TMP/tensorflow/
podman cp ./models/research/object_detection/configs/tf2/ssd_efficientdet_d0_512x512_coco17_tpu-8.config 5d3ab326d30b:/home/tensorflow/models/research/object_detection/configs/tf2/ssd_efficientdet_d0_512x512_coco17_tpu-8.config
```

inside:
```
cd /home/tensorflow/ tar xvf /home/tensorflow/models/research/object_detection/efficientdet_d0_coco17_tpu-32.tar.gz
#
#model_main_tf2.sh /home/tensorflow/models/research/
cd /home/tensorflow/models/research/
protoc object_detection/protos/*.proto --python_out=.
python -m pip install .
```
## running it...
```
#[jfclere@fedora TMP]$ podman ps
#CONTAINER ID  IMAGE                                     COMMAND     CREATED      STATUS          PORTS       NAMES
#5d3ab326d30b  quay.io/jfclere/kibble_tensorflow:latest  bash        4 hours ago  Up 4 hours ago              eager_bartik

podman exec  -it eager_bartik bash

root@5d3ab326d30b:/home/tensorflow/models/research/object_detection# tensorboard --logdir=/home/tensorflow/TMP/train/train/
```
