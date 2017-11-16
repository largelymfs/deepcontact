#################################################################################
#     File Name           :     hhblits_runner.py
#     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-17 22:30]
#     Last Modified       :     [2017-11-15 16:25]
#     Description         :      
#################################################################################

import util
import os
import string


class HHBlitsRunner:
    def __init__(self, config):
        self.config = config

    def run(self):
        print "-" * 60
        print "Running HHBlits"
        self._run()
        self.save_msa()
        print "Done\n"

    def _run(self):
        hh_config = self.config['hhblits']

        id = self.config['id']
        input_file = self.config['path']['input']
        output_file = os.path.join(self.config['path']['output'], id + '.a3m')
        log_name = os.path.join(self.config['path']['output'], id + '.hhblog')
        args = [hh_config['command'],
                '-i', input_file,
                '-d', hh_config['uniprot_db'],
                '-oa3m', output_file,
                '-n', str(hh_config['n_iters']),
                '-maxfilt', str(hh_config['maxfilt']),
                '-diff', str(hh_config['diff']),
                '-id', str(hh_config['id']),
                '-cov', str(hh_config['cov']),
                '-e', str(hh_config['e_value']),
                '-cpu', str(hh_config['n_threads'])]
        util.run_command(args, log_name)

    def save_msa(self):
        id = self.config['id']
        a3m_file = os.path.join(self.config['path']['output'], id + '.a3m')
        aln_file = os.path.join(self.config['path']['output'], id + '.aln')
        with open(a3m_file, 'r') as a3m_f, open(aln_file, 'w') as aln_f:
            for line in a3m_f:
                if not line.startswith('>'):
                    aln_f.write('%s' % line.translate(None, string.ascii_lowercase))
