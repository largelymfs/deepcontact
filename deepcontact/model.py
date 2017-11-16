#! /usr/bin/env python
#################################################################################
#     File Name           :     model.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 12:50]
#     Last Modified       :     [2017-11-15 20:38]
#     Description         :      
#################################################################################

import lasagne
from deepcontact.layers import Feature2dBiasLayer, FeatureCombineLayer, LinearLayer

def stack_conv2D_layer(incoming, filter_size, filter_number):
    '''
        incoming : incoming layer
        filter_size : The Conv2D fitler_size, a list
        filter_number : the Conv2D filter Number, a list
    '''
    last_layer = incoming
    layer_number = len(filter_size)
    assert(len(filter_number) == layer_number)
    res = []
    for id in xrange(layer_number):
        now_layer = lasagne.layers.Conv2DLayer(incoming = last_layer,
                                               num_filters = filter_number[id],
                                               filter_size = filter_size[id],
                                               stride = (1,1),
                                               pad = (filter_size[id] - 1) / 2,
                                               W = lasagne.init.GlorotNormal(),
                                               b = lasagne.init.Constant(0.0),
                                               nonlinearity = lasagne.nonlinearities.linear)
        now_layer = lasagne.layers.BatchNormLayer(incoming = now_layer)
        now_layer = lasagne.layers.NonlinearityLayer(incoming = now_layer,
                                                     nonlinearity = lasagne.nonlinearities.rectify)
        res.append(now_layer)
        last_layer = now_layer
    return res

def stack_conv1D_layer(incoming, filter_size, filter_number):
    '''
        incoming : incoming layer
        filter_size : The Conv1D filter_size, a list
        filter_number : The Conv1D filter number a list
    '''
    last_layer=  incoming
    layer_number = len(filter_size)
    assert(len(filter_number) == layer_number)
    res = []
    for id in xrange(layer_number):
        now_layer = lasagne.layers.Conv1DLayer(incoming = last_layer,
                                               num_filters = filter_number[id],
                                               filter_size = filter_size[id],
                                               stride = 1,
                                               pad  = (filter_size[id] - 1) / 2,
                                               W = lasagne.init.GlorotNormal(),
                                               b = lasagne.init.Constant(0.0),
                                               nonlinearity = lasagne.nonlinearities.linear)
        now_layer = lasagne.layers.BatchNormLayer(incoming = now_layer)
        now_layer = lasagne.layers.NonlinearityLayer(incoming = now_layer,
                                                     nonlinearity = lasagne.nonlinearities.rectify)
        res.append(now_layer)
        last_layer = now_layer
    return res

def make_neural_network(incoming, hidden_number = None):
    input_shape = lasagne.layers.get_output_shape(incoming)
    input_feature_number = input_shape[1]
    max_size = input_shape[2]
    last_layer = incoming
    res = []
    last_input_number = input_feature_number
    for id, now_hidden_number in enumerate(hidden_number):
        now_layer = LinearLayer(incoming = last_layer, max_size = max_size, deepth = last_input_number, num_output = now_hidden_number)
        now_layer = lasagne.layers.BatchNormLayer(now_layer)
        if id == len(hidden_number) - 1:
            now_layer = lasagne.layers.NonlinearityLayer(incoming = now_layer, nonlinearity = lasagne.nonlinearities.sigmoid)
        else:
            now_layer = lasagne.layers.NonlinearityLayer(incoming = now_layer, nonlinearity = lasagne.nonlinearities.rectify)
        last_layer = now_layer
        last_input_number = now_hidden_number
        res.append(now_layer)
    return res

class Model:
    def __init__(self, max_len, feature2d_len, feature1d_len, **kwargs):
        self.max_len = max_len
        self.feature2d_len = feature2d_len
        self.feature1d_len = feature1d_len
    
    def build_model(self, feature2d, feature1d):
        max_len = self.max_len

        ###input###
        input_feature2d = lasagne.layers.InputLayer(shape = (None, self.feature2d_len, max_len, max_len), input_var = feature2d)
        input_feature1d = lasagne.layers.InputLayer(shape = (None, self.feature1d_len, max_len), input_var = feature1d)
        input_feature1d_out = stack_conv1D_layer(input_feature1d, [7, 5], [12, 24])[-1]
        input_feature1d = lasagne.layers.ConcatLayer([input_feature1d, input_feature1d_out], axis = 1)

        ####combine all features
        network_input = FeatureCombineLayer([input_feature2d, input_feature1d])

        network = stack_conv2D_layer(network_input, [5] * 9,[32]*9) 
        network = lasagne.layers.ConcatLayer([network_input, network[2], network[5], network[8]],axis = 1)
        network = Feature2dBiasLayer(network)
        network = make_neural_network(network, [30, 1])[-1]
        return network

