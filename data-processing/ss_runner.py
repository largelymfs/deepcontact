#     File Name           :     ss_runner.py
#     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-17 22:30]
#     Last Modified       :     [2017-11-15 16:50]
#     Description         :      
#################################################################################
import util
import os
import shutil


class SSRunner:
    def __init__(self, config):
        self.config = config

    def run(self):
        self.run_blast()
        self.run_makemat()
        self.run_psipred()
        self.run_psipred_pass2()
        self.run_solvpred()

    def run_blast(self):
        print "-" * 60
        print "Running Blast"

        id = self.config['id']

        fasta_file = self.config["path"]["input"]
        output_name = os.path.join(self.config['path']['output'], id + '.chk')
        log_name = os.path.join(self.config['path']['output'], id + '.blast')

        blast_config = self.config['blast']
        args = [blast_config['command'],
                '-a', str(blast_config['n_threads']),
                '-b', '0',
                '-j', str(blast_config['n_iters']),
                '-h', str(blast_config['e_value']),
                '-d', 'nr',
                '-i', fasta_file,
                '-C', output_name]
        util.run_command(args, log_name)
        print "Done\n"

    def run_makemat(self):
        print "-" * 60
        print "Running Makemat"

        id = self.config['id']

        fasta_file = self.config["path"]["input"]

        try:
            shutil.copy(fasta_file, self.config['path']['output'])
        except shutil.Error:
            pass

        pn_file = os.path.join(self.config['path']['output'], id + '.pn')
        sn_file = os.path.join(self.config['path']['output'], id + '.sn')

        with open(pn_file, 'w') as pn_f:
            pn_f.write(id + '.chk')
        with open(sn_file, 'w') as sn_f:
            sn_f.write(id + '.fasta')
        args = [self.config['makemat']['command'],
                '-P', os.path.join(self.config['path']['output'], id)]

        util.run_command(args)
        print "Done\n"

    def run_psipred(self):
        print "-" * 60
        print "Running PsiPred"

        id = self.config['id']

        fasta_file = self.config["path"]["input"]

        matrix_file = os.path.join(self.config['path']['output'], id + '.mtx')
        ss_file = os.path.join(self.config['path']['output'], id + '.ss')

        args = [self.config['psipred']['command'],
                matrix_file,
                os.path.join(self.config['psipred']['data'], 'weights.dat'),
                os.path.join(self.config['psipred']['data'], 'weights.dat2'),
                os.path.join(self.config['psipred']['data'], 'weights.dat3')]
        util.run_command(args, ss_file)
        print "Done\n"

    def run_psipred_pass2(self):
        print "-" * 60
        print "Running PsiPredPass2"

        id = self.config['id']

        ss_file = os.path.join(self.config['path']['output'], id + '.ss')
        ss2_file = os.path.join(self.config['path']['output'], id + '.ss2')
        horiz_file = os.path.join(self.config['path']['output'], id + '.horiz')

        args = [self.config['psipred_pass2']['command'],
                os.path.join(self.config['psipred']['data'], 'weights_p2.dat'),
                str(self.config['psipred_pass2']['n_iters']),
                str(self.config['psipred_pass2']['DCA']),
                str(self.config['psipred_pass2']['DCB']),
                ss2_file,
                ss_file]

        util.run_command(args, horiz_file)
        print "Done\n"

    def run_solvpred(self):
        print "-" * 60
        print "Running Solvpred"

        id = self.config['id']

        matrix_file = os.path.join(self.config['path']['output'], id + '.mtx')
        solv_file = os.path.join(self.config['path']['output'], id + '.solv')
        args = [self.config['solvpred']['command'],
                matrix_file,
                self.config['solvpred']['data']]
        util.run_command(args, solv_file)
        print "Done\n"
