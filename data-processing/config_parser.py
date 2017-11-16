#################################################################################
#     File Name           :     config.py #     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-16 17:15]
#     Last Modified       :     [2017-11-15 16:17]
#     Description         :      
#################################################################################


import yaml
import os
import collections


def parse(default_config_yaml, input_sequence, output_dir):
    default_config = yaml.load(open(default_config_yaml))
    default_config["path"]["input"] = input_sequence
    default_config["path"]["output"] = output_dir
    output_name = os.path.basename(input_sequence)
    if output_name.endswith('.fasta'):
        output_name = output_name[:-6]
    default_config["id"] = output_name
    return default_config

def build_missing_component(config, dataset_name):
    if 'path' not in config or 'output_base' not in config['path']:
        return
    gen_default_path(config, 'id_list', dataset_name + '.id_list')
    gen_default_path(config, 'sequence_dir', dataset_name + '_fasta')
    gen_default_path(config, 'hhblits_result', dataset_name + '_hhblits')
    gen_default_path(config, 'ccmpred_result', dataset_name + '_ccmpred')
    gen_default_path(config, 'freecontact_result', dataset_name + '_freecontact')
    gen_default_path(config, 'psicov_result', dataset_name + '_psicov')
    gen_default_path(config, 'alnstats_result', dataset_name + '_alnstats')
    gen_default_path(config, 'ss_result', dataset_name + '_ss')
    gen_default_path(config, 'metapsicov_result', dataset_name + '_metapsicov_result')
    gen_default_path(config, 'freecontact_psicov_result', dataset_name + '_freecontact_psicov')
    gen_default_path(config, 'jackhmmer_result', dataset_name + '_jackhmmer')
    gen_default_path(config, 'ground_truth_result', dataset_name + '_ground_truth')
    gen_default_path(config, 'precision_all', dataset_name + '_precision_all.json')
    gen_default_path(config, 'precision_summary', dataset_name + '_precision_summary.json')
    gen_default_path(config, 'hhmake_result', dataset_name + '_hhmake')
    gen_default_path(config, 'tmscore_result', dataset_name + '_tmscore')
    if 'gen_feature_with_jackhmmer' in config and config['gen_feature_with_jackhmmer']:
        config['path']['msa_result'] = config['path']['jackhmmer_result']
        config['a3m_suffix'] = '.pseudo_a3m'
    else:
        config['path']['msa_result'] = config['path']['hhblits_result']
        config['a3m_suffix'] = '.a3m'
    return config


def gen_default_path(config, key_name, default_path):
    if key_name not in config['path']:
        config['path'][key_name] = os.path.join(config['path']['output_base'], default_path)
