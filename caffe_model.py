from __future__ import division
import caffe
import numpy as np
import re
import os
import math
from PIL import Image


def initialize_caffe(run_model):
    caffe.set_mode_gpu()

    path = "./model/"
    if (run_model == 1):
        model = path + "classifier_deploy.prototxt"
        weights = path + "snapshots/classifier/aws_class_mcaug_model_iter_9000.caffemodel"

    net = caffe.Net(model, weights, caffe.TEST)
    return net


def preprocessing(net, run_model):
    # Convert mean's .binaryproto into .npy
    mean_blob = caffe.proto.caffe_pb2.BlobProto()
    path = "./input/"
    if (run_model == 1):
        path += "mean.binaryproto"

    mean_proto = open(path, 'rb').read()
    mean_blob.ParseFromString(mean_proto)
    nd_mean_proto = np.array(caffe.io.blobproto_to_array(mean_blob))[0]
    mu = nd_mean_proto.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
    print 'mean-subtracted values:', zip('BGR', mu)

    # Load input and configure preprocessing
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2,0,1))     # move image channels to outermost dimension
    # transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR (unnecessary since our input is from OpenCV which already has it BGR)
    transformer.set_mean('data', mu)               # subtract the dataset-mean value in each channel
    transformer.set_raw_scale('data', 255.0)       # rescale from [0, 1] to [0, 255]

    net.blobs['data'].reshape(1,3,227,227)
    return net, transformer


def predict(net, run_model, transformer, frame):
    LABELS = np.arange(-45, 46)  # Truth labels
    net.blobs['data'].data[...] = transformer.preprocess('data', frame)
    out = net.forward()
    pred_c = np.argmax(out['prob'][0])
    # pred_c = out['prob'][0].argsort()[-5:][::-1]  # Top 5 classes
    pred = LABELS[pred_c]
    return pred, out


def convert_regress(pred_r, LABELS):
    pred_dec, pred_int = math.modf(pred_r)
    label = LABELS[int(pred_int)]
    pred = label + abs(pred_dec)
    return pred