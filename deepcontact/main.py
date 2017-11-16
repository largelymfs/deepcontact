#! /usr/bin/env python
#################################################################################
#     File Name           :     main.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 13:05]
#     Last Modified       :     [2017-11-16 02:18]
#     Description         :      
#################################################################################
from deepcontact.model import Model
import theano.tensor as T
import theano, lasagne, numpy as np
import cPickle, sys

def load_model(output_layer, model_file = "./deepcontact/models/model.npz"):
    with np.load(model_file) as f:
        param_values = [f['arr_%d' % i] for i in range(len(f.files))]
    param_values = list(param_values[0])
    lasagne.layers.set_all_param_values(output_layer, param_values)

def main(feature_2d = None, feature_1d = None, output_filename = None, feature_pickle_filename = None):
    if feature_2d is None and feature_1d is None:
        with open(feature_pickle_filename, "rb") as fin:
            feature2d_value, feature1d_value, protein_length = cPickle.load(fin)
    else:
        feature2d_value, feature1d_value = feature_2d, feature_1d
    m = Model(max_len = feature2d_value.shape[-1], 
              feature2d_len = feature2d_value.shape[0], 
              feature1d_len = feature1d_value.shape[0])
    feature2d = T.tensor4("feature2d")
    feature1d = T.tensor3("feature1d")
    network = m.build_model(feature2d, feature1d)
    output = lasagne.layers.get_output(network, deterministic = True)
    pred_fn = theano.function([feature2d, feature1d], output, updates = None)
    load_model(output_layer = network)
    prediction = pred_fn([feature2d_value], [feature1d_value])[0][0][:protein_length, : protein_length]
    if output_filename is None:
        output_filename = './tmp_output/prediction.pkl'

    with open(output_filename, "wb") as fout:
        cPickle.dump(prediction, fout)

if __name__=="__main__":
    feature_pickle_filename = sys.argv[1]
    output_filename = sys.argv[2]
    main(feature_pickle_filename = feature_pickle_filename, output_filename = output_filename)
