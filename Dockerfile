FROM tensorflow/tensorflow:2.2.0-gpu

ARG DEBIAN_FRONTEND=noninteractive

RUN rm /etc/apt/sources.list.d/cuda.list
RUN rm /etc/apt/sources.list.d/nvidia-ml.list

# Install apt dependencies
RUN apt-get update && apt-get install -y \
    git \
    gpg-agent \
    python3-cairocffi \
    protobuf-compiler \
    python3-pil \
    python3-lxml \
    python3-tk \
    wget \
    python3-pip \
    vim

RUN pip install --upgrade cmake

# Install gcloud and gsutil commands
# https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu
RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

# JFC stuff
#COPY ./research/object_detection/model_main_tf2.sh /home/tensorflow/models/research/object_detection
#RUN mkdir /home/jfclere/TMP/tensorflow
#RUN mkdir /home/jfclere/TMP/models/research/object_detection/configs/tf2/
#COPY ./research/object_detection/configs/tf2/ssd_efficientdet_d0_512x512_coco17_tpu-8.config /home/jfclere/TMP/models/research/object_detection/configs/tf2/
#COPY ./TMP /home/jfclere/TMP/tensorflow/TMP

# Add new user to avoid running as root
RUN useradd -ms /bin/bash tensorflow
#RUN chown tensorflow  -r /home/jfclere/TMP/tensorflow
USER tensorflow
WORKDIR /home/tensorflow

# Copy this version of of the model garden into the image
COPY --chown=tensorflow . /home/tensorflow/models

# Compile protobuf configs
RUN (cd /home/tensorflow/models/research/ && protoc object_detection/protos/*.proto --python_out=.)
WORKDIR /home/tensorflow/models/research/

RUN cp object_detection/packages/tf2/setup.py ./
ENV PATH="/home/tensorflow/.local/bin:${PATH}"

RUN python -m pip install -U pip
RUN python -m pip install .


ENV TF_CPP_MIN_LOG_LEVEL 3
