#################################################################################
#     File Name           :     fasta_spliter.py
#     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-17 17:09]
#     Last Modified       :     [2016-04-17 23:39]
#     Description         :      
#################################################################################
import re

import config_parser
import util
import os
from Bio import SeqIO


class FastaFilter:
    def __init__(self, config):
        self.config = config

    def all_sequences(self):
        return SeqIO.parse(self.config["path"]["fasta_sequence"], "fasta")

    def run(self):
        print "="*60
        print "Preprocessing fasta sequences"
        self.save_seqs()
        print "Done\n"

    def save_seqs(self):
        if not os.path.exists(self.config['path']['id_list']):
            self.save_id_list()
        util.make_dir_if_not_exist(self.config['path']['sequence_dir'])

        sequences = SeqIO.to_dict(self.all_sequences())
        with open(self.config['path']['id_list']) as f_in:
            for line in f_in:
                seq_id = line.strip().split()[0]
                seq_record = sequences[seq_id]
                with open(os.path.join(self.config['path']['sequence_dir'], seq_record.id + '.fasta'), 'w') as f_out:
                    SeqIO.write(seq_record, f_out, 'fasta')

    def save_id_list(self):
        with open(self.config['path']['id_list'], 'w') as f_out:
            for seq_record in self.all_sequences():
                if self.config['is_scop_data']:
                    family = ''
                    regex = re.compile(r'[a-z]\.[0-9]*\.[0-9]*')
                    match = regex.search(seq_record.description)
                    if match:
                        family = match.group(0)
                    print >> f_out, seq_record.id, family
                else:
                    print >> f_out, seq_record.id


if __name__ == '__main__':
    config = config_parser.parse('../config_files/default.yaml', '../config_files/user.yaml')
    f = FastaFilter(config)
    f.save_seqs()
