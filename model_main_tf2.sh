export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
#python model_main_tf2.py \
#    --pipeline_config_path=/home/jfclere/TMP/models/research/object_detection/configs/tf2/ssd_efficientdet_d0_512x512_coco17_tpu-8.config \
#    --model_dir=/home/jfclere/TMP/tensorflow/TMP/train \
#    --alsologtostderr
#
#export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python model_main_tf2.py \
    --pipeline_config_path=/home/tensorflow/models/research/object_detection/configs/tf2/ssd_efficientdet_d0_512x512_coco17_tpu-8.config \
    --model_dir=/home/tensorflow/TMP/train \
    --alsologtostderr
