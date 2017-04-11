'''
Creates and stores training and validation sets with labels.

Requirements:
1. Training images must be stored in ./train/ as jpg
2. Validation images must be stored in ./test/ as jpg
3. Filenames must include the labeled angle of the image right before file extension
    Ex: coldwater_001_-11.jpg
    This would be a -11 degree label

Usage: python create_lmdb.py
'''

import os
import glob
import random
import numpy as np
import cv2
import caffe
from caffe.proto import caffe_pb2
import lmdb
import re


#Size of images
IMAGE_WIDTH = 227
IMAGE_HEIGHT = 227
LABELS = np.arange(-45, 46)


def transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT):
    #Histogram Equalization
    img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
    img[:, :, 1] = cv2.equalizeHist(img[:, :, 1])
    img[:, :, 2] = cv2.equalizeHist(img[:, :, 2])

    #Image Resizing
    img = cv2.resize(img, (img_width, img_height), interpolation = cv2.INTER_CUBIC)

    return img


def make_datum(img, label):
    #image is numpy.ndarray format. BGR instead of RGB
    return caffe_pb2.Datum(
        channels=3,
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT,
        label=label,
        data=np.rollaxis(img, 2).tostring())


def get_label(img_path):
    label = []
    for i in img_path[-5::-1]:
        if i != "_":
            label.append(i)
        else:
            break
    label = ''.join(label[::-1])
    label = int(re.sub('[^0-9,-]','', label))
    converted_label = np.where(LABELS==label)[0][0]
    return converted_label


train_lmdb = "../lmdb_train"
validation_lmdb = "../lmdb_val"

os.system('rm -rf  ' + train_lmdb)
os.system('rm -rf  ' + validation_lmdb)

train_data = [img for img in glob.glob("../train/*jpg")]
test_data = [img for img in glob.glob("../test/*jpg")]


print 'Creating train_lmdb'
in_db = lmdb.open(train_lmdb, map_size=int(1.1e10))
with in_db.begin(write=True) as in_txn:
    for in_idx, img_path in enumerate(train_data):
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT)
        label = get_label(img_path)
        datum = make_datum(img, label)
        in_txn.put('{:0>5d}'.format(in_idx), datum.SerializeToString())
        print '{:0>5d}'.format(in_idx) + ':' + img_path
in_db.close()


print '\nCreating validation_lmdb'
in_db = lmdb.open(validation_lmdb, map_size=int(6e9))
with in_db.begin(write=True) as in_txn:
    for in_idx, img_path in enumerate(test_data):
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT)
        label = get_label(img_path)
        datum = make_datum(img, label)
        in_txn.put('{:0>5d}'.format(in_idx), datum.SerializeToString())
        print '{:0>5d}'.format(in_idx) + ':' + img_path
in_db.close()


print '\nFinished processing all images'