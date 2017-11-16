#! /usr/bin/env python
#################################################################################
#     File Name           :     ./data_util.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 13:32]
#     Last Modified       :     [2017-11-15 14:17]
#     Description         :      
#################################################################################

import numpy as np
import theano.tensor as T
import h5py, lasagne
DTYPE = 'float32'

def iterate(input_size, batchsize, shuffle = True, data_file = None):
    fin = h5py.File(data_file)
    task_number, _ , max_len = fin['label'].shape
    feature2d_number = fin['feature2d'].shape[1]
    feature1d_number = fin['feature1d'].shape[1]

    buf_feature2d = np.zeros((batchsize, feature2d_number, max_len, max_len), dtype = DTYPE) 
    buf_feature1d = np.zeros((batchsize, feature1d_number, max_len), dtype = DTYPE)
    buf_label = np.zeros((batchsize, max_len, max_len), dtype = DTYPE)
    buf_length = np.zeros((batchsize, 1), dtype = DTYPE)
    buf_weight = np.zeros((batchsize, max_len, max_len), dtype = DTYPE)

    if shuffle:
        indices = np.arange(input_size)
        np.random.shuffle(indices)
    else:
        indices = np.arange(input_size)

    data_label = fin['label']
    data_weight = fin['weight']
    data_length = fin['length']
    data_feature2d = fin['feature2d']
    data_feature1d = fin['feature1d']

    start_idx = 0
    for start_idx in xrange(0, input_size - batchsize + 1, batchsize):
        now_index = indices[start_idx : start_idx + batchsize]
        for id in xrange(len(now_index)):
            buf_feature1d[id] = data_feature1d[now_index[id]]
            buf_feature2d[id] = data_feature2d[now_index[id]]
            buf_length[id] = data_length[now_index[id]]
            buf_weight[id] = data_weight[now_index[id]]
            buf_label[id] = data_label[now_index[id]]
        yield buf_feature1d, buf_feature2d, buf_label, buf_weight, buf_length

    if input_size % batchsize != 0:
        start_idx += batchsize
        now_index = indices[start_idx : ]
        buf_feature1d.fill(0.0)
        buf_feature2d.fill(0.0)
        buf_length.fill(0.0)
        buf_weight.fill(0.0)
        buf_label.fill(0.0)
        for id in xrange(len(now_index)):
            buf_feature1d[id] = data_feature1d[now_index[id]]
            buf_feature2d[id] = data_feature2d[now_index[id]]
            buf_length[id] = data_length[now_index[id]]
            buf_weight[id] = data_weight[now_index[id]]
            buf_label[id] = data_label[now_index[id]]
        l = len(now_index)
        yield buf_feature1d[:l], buf_feature2d[:l], buf_label[:l], buf_weight[:l], buf_length[:l]
    fin.close()

