import multiprocessing
import subprocess32
import os

from Bio import SeqIO
from Bio.Data.SCOPData import protein_letters_3to1
from Bio.PDB import PDBParser

DEVNULL = open(os.devnull, 'wb')


class UnknownResidueError(Exception):
    pass

def _work(args_and_log):
    args, log_file = args_and_log
    print " ".join(args)
    if log_file:
        with open(log_file, 'w') as the_log:
            p = subprocess32.Popen(args, stdout=the_log, stderr=DEVNULL)
            p.wait()
    else:
        p = subprocess32.Popen(args, stdout=DEVNULL)
        p.wait()

def run_command(args, log_file=None):
    _work([args, log_file])


class PopenPool:
    def __init__(self, n_workers=8):
        self.pool = multiprocessing.Pool(processes=n_workers)
        self.jobs = list()

    def add_job(self, args, log_file=None, timeout=None):
        self.jobs.append([args, log_file, timeout])

    def start(self):
        self.pool.imap_unordered(_work, self.jobs)

    def wait(self):
        self.pool.close()
        self.pool.join()


def make_dir_if_not_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_id_list(config):
    ret = list()
    with open(config['path']['id_list']) as f_in:
        for line in f_in:
            if line:
                ret.append(line.strip().split()[0])
    return ret


def get_fasta_path(config, id):
    return os.path.join(config['path']['sequence_dir'], id + '.fasta')


def get_ground_truth_path(config, id):
    ground_truth = os.path.join(config['path']['ground_truth_result'], id + '.ground_truth')
    return ground_truth


def get_ground_truth_exclusion_set(config):
    ret = set()
    with open(os.path.join(config['path']['ground_truth_result'], 'ground_truth_error.list')) as f_in:
        for line in f_in:
            if line:
                ret.add(str(line.split(':')[0]))
    return ret


def get_pdb_length(structure):
    return sum(1 for _ in structure.get_residues())


def build_peptides(structure):
    peptides = list()
    curr_peptide = list()
    gap_sizes = list()
    curr_peptide_index = None
    for residue in structure.get_residues():
        if curr_peptide_index is None:
            try:
                curr_peptide.append(protein_letters_3to1[residue.get_resname()])
            except KeyError:
                raise UnknownResidueError('Residue %s is not known' % residue.get_resname())
            curr_peptide_index = residue.get_id()[1]
        else:
            residue_id = residue.get_id()[1]
            if residue_id - curr_peptide_index == 1:
                try:
                    curr_peptide.append(protein_letters_3to1[residue.get_resname()])
                except KeyError:
                    raise UnknownResidueError('Residue %s is not known' % residue.get_resname())
            else:
                gap_sizes.append(residue_id - curr_peptide_index - 1)
                peptides.append(''.join(curr_peptide))
                curr_peptide = [protein_letters_3to1[residue.get_resname()]]
            curr_peptide_index = residue_id
    if curr_peptide:
        peptides.append(''.join(curr_peptide))
    return peptides, gap_sizes


def get_sequence(config, code):
    seq_file = get_fasta_path(config, code)
    with open(seq_file) as f_in:
        sequences = SeqIO.parse(f_in, 'fasta')
        seq = sequences.next().seq
    return str(seq).upper()


def get_structure_file_path(config, code):
    if config['is_pdb_scop_style']:
        struct_file = os.path.join(config["path"]["pdb_dir"], code[2:4], code + ".ent")
    else:
        struct_file = os.path.join(config["path"]["pdb_dir"], code + ".pdb")
    return struct_file


def get_structure(config, code):
    parser = PDBParser()
    struct_file = get_structure_file_path(config, code)
    structure = parser.get_structure(code, struct_file).get_list()[0]
    return structure


if __name__ == '__main__':
    pool = PopenPool(6)
    for i in range(24):
        pool.add_job(['bash', 'test.sh'], 'test.txt')
    pool.start()
    print 'start'
    pool.wait()
    print 'ok'
