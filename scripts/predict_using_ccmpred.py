#! /usr/bin/env python
#################################################################################
#     File Name           :     predict_using_ccmpred.py
#     Created By          :     yang
#     Creation Date       :     [2018-06-15 20:12]
#     Last Modified       :     [2018-06-15 20:47]
#     Description         :      
#################################################################################

from deepcontact.main import load_model
from deepcontact.model import ModelCCMPRED
import theano.tensor as T
import theano, lasagne, numpy as np
import cPickle, sys


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description = "predict contact using ccmpred-like input")
    parser.add_argument('--input_filename', type = str, default = None) 
    parser.add_argument('--output_filename', type = str, default = None) 
    return parser.parse_args()

def normalize(data):
    mean = np.mean(data)
    std = np.std(data)
    data -= mean
    if std != 0:
        data /= std
    return data

if __name__=="__main__":
    args = parse_args()
    input_filename = args.input_filename
    output_filename = args.output_filename
    
    ccmpred_feature = np.loadtxt(input_filename).astype(np.float32)
    ccmpred_feature = normalize(ccmpred_feature)
    protein_length = ccmpred_feature.shape[0]

    ccmpred_feature_for_nn = np.array([[ccmpred_feature]]).astype(np.float32)

    model = ModelCCMPRED(max_len = protein_length, feature2d_len = 1)

    feature2d = T.tensor4('feature2d')
    network = model.build_model(feature2d)
    output = lasagne.layers.get_output(network, deterministic = True)
    pred_fn = theano.function([feature2d], output, updates = None)
    load_model(output_layer = network, model_file = "./deepcontact/models/model_ccmpred.npz")

    prediction = pred_fn(ccmpred_feature_for_nn)[0][0][:protein_length, :protein_length]
    np.savetxt(output_filename, prediction)

