###############################################################################
#     File Name           :     jackhmmer_runner.py
#     Created By          :     Qing Ye
#     Creation Date       :     [2016-04-17 22:30]
#     Last Modified       :     [2017-11-15 18:54]
#     Description         :      
#################################################################################
import util
import string
import os,sys
import subprocess

class Jackhmmer_Runner:
    def __init__(self, config):
        self.config = config

    def run(self):
        print "-" * 60
        print "Running Jackhmmer"
        self.run_jackhmmer()
        print "Done\n"

        print "Reformating Jackhmmer"
        self.format_jackali()
        print "Done\n"

        print "-" * 60
        print "Running HHfilter"
        self.run_hhfilter()
        print "Done\n"

        print "-" * 60
        print "Reformatting HHfilter"
        self.format_hhfilter()
        print "Done\n"

    def run_jackhmmer(self):
        id = self.config['id']
        fasta_file = self.config['path']['input']

        output_file = os.path.join(self.config['path']['output'], id + '.jackali')
        log_file = os.path.join(self.config['path']['output'], id + '.jacklog')

        args = [self.config['jackhmmer']['command'],
                '-N', str(self.config['jackhmmer']['n_iter']),
                '--cpu', str(self.config['jackhmmer']['n_threads']),
                '--incE', str(self.config['jackhmmer']['inc_E']),
                '-A', output_file,
                fasta_file,
                self.config['jackhmmer']['uniref_db']]

        util.run_command(args, log_file)

    def format_jackali(self):
        id = self.config['id']

        jackali_file = os.path.join(self.config['path']['output'], id + '.jackali')
        pseudo_a3m_file = os.path.join(self.config['path']['output'], id + '.a3m')
        all_seqs = dict()

        input_seq_id = None

        with open(jackali_file) as f_in:
            for line in f_in:
                if line.strip() and not line.startswith('#') and len(line.strip().split()) == 2:
                    seq_id, seq = line.strip().split()
                    if not input_seq_id:
                        input_seq_id = seq_id
                    if seq_id in all_seqs:
                        all_seqs[seq_id].append(seq)
                    else:
                        all_seqs[seq_id] = [seq]
        for k in all_seqs.iterkeys():
            all_seqs[k] = ''.join(all_seqs[k])
        print all_seqs.keys()
        with open(pseudo_a3m_file, 'w') as f_out:
            f_out.write('>%s\n' % input_seq_id)
            f_out.write('%s\n' % all_seqs[input_seq_id])
            for k, v in all_seqs.iteritems():
                if k == id:
                    continue
                f_out.write('>%s\n' % k)
                f_out.write('%s\n' % v)
        subprocess.call('rm ' + jackali_file, shell=True)

    def count_number(self, filename):
        with open(filename) as fin:
          while True:
              l = fin.readline()
              if not l:
                break
              words = l.strip().split()
              if len(words)!=3:
                continue
              if words[0] == '@@' and words[1].strip() == 'Round:' and words[2].strip() == '3':
                break
          for _ in xrange(8):
              fin.readline()
          cnt = 0
          for l in fin:
            words = l.strip().split()
            if len(words) == 0:
              break
            evalue = words[0]
            if evalue == '+':
              evalue = words[1]
            evalue = float(evalue)
            if evalue >=0.1:
              break
            else:
              cnt += 1
        return cnt


    def format_jackali_with_filter(self):
        id = self.config['id']

        jackali_file = os.path.join(self.config['path']['output'], id + '.jackali')
        jacklog_file = os.path.join(self.config['path']['output'], id + ".jacklog")
        available_number = self.count_number(jacklog_file)
        pseudo_a3m_file = os.path.join(self.config['path']['output'], id + '.a3m')
        all_seqs = dict()
        with open(jackali_file) as f_in:
            for line in f_in:
                if len(all_seqs.keys()) == available_number:
                  break
                if line.strip() and not line.startswith('#') and len(line.strip().split()) == 2:
                    seq_id, seq = line.strip().split()
                    if seq_id in all_seqs:
                        all_seqs[seq_id].append(seq)
                    else:
                        all_seqs[seq_id] = [seq]
        for k in all_seqs.iterkeys():
            all_seqs[k] = ''.join(all_seqs[k])
        with open(pseudo_a3m_file, 'w') as f_out:
            f_out.write('>%s\n' % id)
            f_out.write('%s\n' % all_seqs[id])
            for k, v in all_seqs.iteritems():
                if k == id:
                    continue
                f_out.write('>%s\n' % k)
                f_out.write('%s\n' % v)


    def run_hhfilter(self):
        id = self.config['id']

        pseudo_a3m_file = os.path.join(self.config['path']['output'], id + '.a3m')
        output_file = os.path.join(self.config['path']['output'], id + '.filtered')
        args = [self.config['hhfilter']['command'],
                '-id', '90',
                '-M', 'first',
                '-cov', '50',
                '-i', pseudo_a3m_file,
                '-o', output_file]
        util.run_command(args)

    def format_hhfilter(self):
        id = self.config['id']

        hhfiltered_file = os.path.join(self.config['path']['output'], id + '.filtered')
        aln_file = os.path.join(self.config['path']['output'], id + '.aln')

        with open(hhfiltered_file) as f_in:
            contents = f_in.read()
            seqs = contents.split('\n>')
            first_seq = seqs[0].split('\n')[1]
            is_not_gap = list()
            for i, l in enumerate(first_seq):
                if l != '-':
                    is_not_gap.append(i)
            alignments = [''.join([first_seq[i] for i in is_not_gap])]

            for seq in seqs[1:]:
                s = seq.split('\n')[1]
                s = s.translate(None, string.ascii_lowercase)
                alignments.append(''.join([s[i] for i in is_not_gap]))
        
        subprocess.call('rm '+ hhfiltered_file, shell=True)
        with open(aln_file, 'w') as f_out:
            for alignment in alignments:
                f_out.write('%s\n' % alignment)
