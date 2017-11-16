#! /usr/bin/env python
#################################################################################
#     File Name           :     ./layer.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 12:51]
#     Last Modified       :     [2017-11-15 13:09]
#     Description         :     some layers definition
#################################################################################

import lasagne, theano
import numpy as np
import theano.tensor as T
DTYPE = "float32"

class FeatureCombineLayer(lasagne.layers.MergeLayer):
    def __init__(self, incomings, **kwargs):
        super(FeatureCombineLayer, self).__init__(incomings, **kwargs)
        max_size = self.output_shape[2]
        self.one = T.ones((1, max_size), dtype=DTYPE)
    
    def get_output_shape_for(self, input_shapes, **kwargs):
        return (input_shapes[0][0], input_shapes[0][1] + input_shapes[1][1] * 2, input_shapes[0][2], input_shapes[0][3])

    def get_output_for(self, input,**kwargs):
        feature2d = input[0]
        feature1d = input[1]
        feature1d_h = feature1d.dimshuffle(0, 1, 2, 'x')
        feature1d_h = T.tensordot(feature1d_h, self.one, [[3], [0]])
        feature1d_v = feature1d_h.dimshuffle(0, 1, 3, 2)

        return T.concatenate([feature2d, feature1d_h, feature1d_v], axis = 1) 

class Feature2dBiasLayer(lasagne.layers.Layer):
    def __init__(self, incoming = None, **kwargs):
        super(Feature2dBiasLayer,self).__init__(incoming, **kwargs)
        self.max_size = self.output_shape[2]
        ###generate zero
        self.bias = np.zeros((7, self.max_size, self.max_size), dtype = DTYPE)
        for i in xrange(self.max_size):
            for j in xrange(self.max_size):
                delta = abs(i - j)
                if delta < 14: 
                    t = 0
                elif delta < 18:
                    t = 1
                elif delta < 23:
                    t = 2
                elif delta < 28:
                    t = 3
                elif delta < 38:
                    t = 4
                elif delta < 48:
                    t = 5
                else:
                    t = 6
                self.bias[t, i, j] = 1.0
        self.bias = theano.shared(self.bias)
        self.bias = self.bias.dimshuffle('x', 0, 1, 2)

    def get_output_shape_for(self, input_shape, **kwargs):
        return (input_shape[0], input_shape[1] + 7, input_shape[2], input_shape[3])
    
    def get_output_for(self, input, **kwargs):
        batch_size = input.shape[0]
        one = T.ones((batch_size, 1), dtype=DTYPE)
        tmp = T.tensordot(one, self.bias, [[1], [0]])
        return T.concatenate([input, tmp], axis = 1)

class LinearLayer(lasagne.layers.Layer):
    def __init__(self, incoming = None, max_size = 256, deepth = 25, W = lasagne.init.GlorotUniform(), b = lasagne.init.Constant(0.0),num_output = 1,**kwargs):
        super(LinearLayer, self).__init__(incoming, **kwargs)
        self.max_size = max_size
        self.deepth = deepth
        self.num_output = num_output
        self.W = self.add_param(W,(self.deepth,num_output), name = "W")
        self.b = self.add_param(b, (num_output,), name = 'b')

    def get_output_shape_for(self, input_shape, **kwargs):
        return (input_shape[0], self.num_output, input_shape[2], input_shape[3])

    def get_output_for(self, input, **kwargs):
        tmp = T.tensordot(input, self.W, [[1],[0]]).dimshuffle(0, 3, 1, 2)
        return tmp + self.b[None,:,None,None]

