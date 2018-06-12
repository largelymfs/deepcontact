#! /usr/bin/env python
#################################################################################
#     File Name           :     feature_gen.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 16:59]
#     Last Modified       :     [2018-06-12 08:58]
#     Description         :      
#################################################################################
import yaml, h5py, os, sys
from deepcontact.feature_parser import *
import cPickle
DTYPE = 'float32'

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description = 'generate feature file given a set of configuration')
    parser.add_argument('configure_file_name', type = str, help='configuration file name ')
    args = parser.parse_args()
    return args

def load_config(filename):
    with open(filename) as fin:
        data = yaml.load(fin)
        global_setting = data['general']
        data.pop('general')
        feature_set = data
    return feature_set, global_setting

def generate_feature_2d(feature_name, feature_dir, suffix, length, parser_name, global_setting):
    max_len = int(global_setting['max_len'])
    ret = np.zeros((length, max_len, max_len))
    parsing_function = function_map[parser_name]
    input_file_name = os.path.join(feature_dir, 'test.'+suffix)
    data = parsing_function(input_file_name, max_len)
    if data is None:
        print "There is a error in %s" % input_file_name
    ret[:, :, :] = data[:, :, :]
    return ret

def generate_feature_1d(feature_name, feature_dir, suffix, length, parser_name, global_setting):
    max_len = int(global_setting['max_len'])
    ret = np.zeros((length, max_len))
    parsing_function = function_map[parser_name]
    input_file_name = os.path.join(feature_dir, "test."+suffix)
    data = parsing_function(input_file_name, max_len)
    if data is None:
        print "There is a error in %s" % input_file_name
    ret[:, :] = data[:, :]
    return ret

def generate_feature_0d(feature_name, feature_dir, suffix, length, parser_name, global_setting):
    max_len = int(global_setting['max_len'])
    ret = np.zeros((max_len))
    parsing_function = function_map[parser_name]
    input_file_name = os.path.join(feature_dir, 'test.'+suffix)
    data = parsing_function(input_file_name, max_len)
    if data is None:
        print "There is a error in %" % input_file_name
    ret[:] = data[:]
    return ret

def get_protein_length_by_ccmpred(feature_dir):
    protein_name = os.path.join(feature_dir, 'test.ccmpred')
    length = np.loadtxt(protein_name).shape[0]
    return length

if __name__=="__main__":
    #arg = parse_args()
    feature_config = sys.argv[1]
    feature_dir = sys.argv[2]
    output_filename = sys.argv[3]

    feature_set, global_setting = load_config(feature_config)
    max_len = global_setting['max_len']
    feature_map = {}
    for task_name in feature_set.keys():
        setting = feature_set[task_name]
        suffix = setting['suffix']
        length = setting['length']
        parser_name = setting['parser_name']
        feature_type = setting['type']
        if task_name == 'ccmpred':
            protein_length = get_protein_length_by_ccmpred(feature_dir)
        if 'skip' in setting:
            skip = bool(setting['skip'])
        else:
            skip = False
        if skip:
            continue
        if feature_type=='2d':
            ret = generate_feature_2d(task_name, feature_dir, suffix, length, parser_name, global_setting)
            feature_map[task_name] = (ret, feature_type)
        elif feature_type == '1d':
            ret = generate_feature_1d(task_name, feature_dir, suffix, length, parser_name, global_setting)
            feature_map[task_name] = (ret, feature_type)
        else:
            ret = generate_feature_0d(task_name, feature_dir, suffix, length, parser_name, global_setting)
            feature_map[task_name] = (ret, feature_type)
    
    combine_feature_list_2d = ['ccmpred', 'pairstats', 'evfold']
    combine_feature_list_1d = ['neff', 'ss2', 'solv', 'colstats', 'evfold_std', 'ccmpred_std']
    combine_feature_list_2d = [x for x in combine_feature_list_2d if x in feature_map]
    combine_feature_list_1d = [x for x in combine_feature_list_1d if x in feature_map]
    
    total_feature_length = 0
    for feature_name_2d in combine_feature_list_2d:
        total_feature_length += feature_map[feature_name_2d][0].shape[0]
    feature_2d = np.zeros((total_feature_length, max_len, max_len)).astype(DTYPE)
    cnt = 0
    for feature_name_2d in combine_feature_list_2d:
        current_feature_value = feature_map[feature_name_2d][0]
        feature_2d[cnt:cnt + current_feature_value.shape[0], :, :] = current_feature_value[:, :, :]
        cnt += current_feature_value.shape[0]
    
    total_feature_length = 0
    for feature_name_1d in combine_feature_list_1d:
        total_feature_length += feature_map[feature_name_1d][0].shape[0]
    feature_1d = np.zeros((total_feature_length, max_len)).astype(DTYPE)
    cnt = 0
    for feature_name_1d in combine_feature_list_1d:
        current_feature_value = feature_map[feature_name_1d][0]
        feature_1d[cnt:cnt + current_feature_value.shape[0], :] = current_feature_value[:,  :]
        cnt += current_feature_value.shape[0]

    with open(output_filename,"wb") as fout:
        cPickle.dump((feature_2d, feature_1d, protein_length), fout)

