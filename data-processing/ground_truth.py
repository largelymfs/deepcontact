import os
import re
import numpy as np
import numpy.linalg as alg
import scipy
import scipy.spatial
import util
import itertools
import multiprocessing
from Bio import SeqIO


class AlignmentError(Exception):
    pass

class PDBError(Exception):
    pass


class GroundTruthBuilder:
    def __init__(self, config):
        self.config = config
        if 'astral206' in self.config['ground_truth'] and self.config['ground_truth']['astral206']:
            self.original_sequences = SeqIO.to_dict(
                    SeqIO.parse(self.config['ground_truth']['original_sequence'], 'fasta'))

    def run(self):
        util.make_dir_if_not_exist(self.config['path']['ground_truth_result'])
        print "-" * 60
        print "Building Ground Truth"
        self._run()
        print "Done\n"

    def _run(self):
        with open(os.path.join(self.config['path']['ground_truth_result'], 'ground_truth_error.list'), 'w') as f_error:
            for id in util.get_id_list(self.config):
                try:
                    if 'heavy_atom' in self.config['ground_truth'] and self.config['ground_truth']['heavy_atom']:
                        truth = self.build_truth_for_one_all_heavy_atom(id)
                    else:
                        truth = self.build_truth_for_one(id)
                except IOError:
                    print >> f_error, "%s: PDB not found" % id
                    continue
                except util.UnknownResidueError as e:
                    print >> f_error, "%s: PDB cannot be parsed due to unknown residue" % id
                    continue
                except AlignmentError:
                    print >> f_error, "%s: PDB sequence does not match fasta sequence" % id
                    continue
                except PDBError:
                    print >> f_error, "%s: PDB has broken residue" % id
                    continue
                output = os.path.join(self.config['path']['ground_truth_result'], id + '.ground_truth')
                np.savetxt(output, truth)

    def build_truth_for_one(self, id):
        index_reference, sequence, structure = self.get_index_ref_seq_and_struct(id)

        residue_positions = GroundTruthBuilder.get_residue_positions(structure)
        pdb_dist_mat = scipy.spatial.distance.squareform(scipy.spatial.distance.pdist(residue_positions, 'euclidean'))

        ret_mat = GroundTruthBuilder.get_fixed_mat(pdb_dist_mat, index_reference, len(sequence))
        ret_mat = self.fix_astral_206_ground_truth(id, ret_mat)
        return ret_mat

    def build_truth_for_one_all_heavy_atom(self, id):
        index_reference, sequence, structure = self.get_index_ref_seq_and_struct(id)

        residue_positions = GroundTruthBuilder.get_residue_positions_all_heavy_atoms(structure)
        pdb_dist_mat = self.make_dist_mat(residue_positions)

        ret_mat = GroundTruthBuilder.get_fixed_mat(pdb_dist_mat, index_reference, len(sequence))
        ret_mat = self.fix_astral_206_ground_truth(id, ret_mat)
        return ret_mat

    def get_index_ref_seq_and_struct(self, id):
        structure = self.get_struct_safe(id)
        peptides, gaps = util.build_peptides(structure)

        sequence = self.get_sequence_safe(id)

        alignment = GroundTruthBuilder.align_seq_with_peptides(sequence, peptides, gaps)
        index_reference = GroundTruthBuilder.pdb_index_to_seq_index(alignment)
        return index_reference, sequence, structure

    def get_sequence_safe(self, id):
        if 'astral206' in self.config['ground_truth'] and self.config['ground_truth']['astral206'] and len(id) != 7:
            sequence = str(self.original_sequences[id[:7]].seq).upper()
        else:
            sequence = util.get_sequence(self.config, id)
        return sequence

    def get_struct_safe(self, id):
        if 'astral206' in self.config['ground_truth'] and self.config['ground_truth']['astral206'] and len(id) != 7:
            structure = util.get_structure(self.config, id[:7])
        else:
            structure = util.get_structure(self.config, id)
        return structure

    def fix_astral_206_ground_truth(self, id, ret_mat):
        if 'astral206' in self.config['ground_truth'] and self.config['ground_truth']['astral206']:
            if len(id) != 7:
                if id.endswith('_1'):
                    ret_mat = ret_mat[:256, :256]
                else:
                    ret_mat = ret_mat[-256:, -256:]
        return ret_mat

    @staticmethod
    def get_fixed_mat(pdb_dist_mat, index_reference, seq_length):
        ret = np.ones((seq_length, seq_length), dtype=np.dtype(float)) * (-1)
        size = pdb_dist_mat.shape[0]
        for i in range(size):
            for j in range(size):
                assert i < size
                assert j < size
                assert index_reference[i] < seq_length
                assert index_reference[j] < seq_length
                ret[index_reference[i]][index_reference[j]] = pdb_dist_mat[i][j]
        return ret

    @staticmethod
    def build_peptides_alignment_regex(peptides, gap_sizes):
        regex = ['.*(', peptides[0], ')']
        for gap_size, peptide in zip(gap_sizes, peptides[1:]):
            # regex.append('.{0,%d}('% gap_size)
            regex.append('.*(')  # for some reason the gaps in pdb of scop is corrupted
            regex.append(peptide)
            regex.append(')')
        regex = ''.join(regex)
        return regex

    @staticmethod
    def align_seq_with_peptides(sequence, peptides, gap_sizes):
        pattern = GroundTruthBuilder.build_peptides_alignment_regex(peptides, gap_sizes)

        regex = re.compile(pattern)
        match = regex.match(sequence)
        if match is None or len(match.groups()) != len(peptides):
            raise AlignmentError('Does not align')

        aligned = []
        last_end = 0
        for i in range(len(match.groups())):
            aligned.append('-' * (match.start(i + 1) - last_end))
            aligned.append(match.groups()[i])
            last_end = match.end(i + 1)
        aligned.append('-' * (len(sequence) - last_end))
        return ''.join(aligned)

    @staticmethod
    def pdb_index_to_seq_index(alignment):
        ret = []
        for seq_index, letter in enumerate(alignment):
            if letter != '-':
                ret.append(seq_index)
        return ret

    @staticmethod
    def get_residue_positions(structure):
        s = structure
        residues = np.zeros((util.get_pdb_length(structure), 3))
        for i, residue in enumerate(s.get_residues()):
            atoms = residue.get_atom()
            for a in atoms:
                if a.get_name() == 'CB':
                    residues[i] = a.get_coord()
            atoms = residue.get_atom()
            if alg.norm(residues[i]) == 0:
                for a in atoms:
                    if a.get_name() == 'CA':
                        residues[i] = a.get_coord()
        return residues

    @staticmethod
    def get_residue_positions_all_heavy_atoms(structure):
        s = structure
        residues = list()
        for i, residue in enumerate(s.get_residues()):
            exclusion = {'C', 'N', 'O'}
            residue_atoms = list()
            for a in residue.get_atom():
                if a.get_name() not in exclusion and 'H' not in a.get_name():
                    residue_atoms.append(a.get_coord())
            residues.append(residue_atoms)
            if len(residue_atoms) == 0:
                raise PDBError('Residue has no heavy atom')
        return residues

    def make_dist_mat(self, residue_positions):
        pool = multiprocessing.Pool(self.config['ground_truth']['n_process'])
        residue_position_args = [(e, residue_positions) for e in residue_positions]
        ret_mat = pool.map(solve_dist_mat, residue_position_args)
        pool.close()
        pool.join()
        ret_mat = np.array(ret_mat)
        return ret_mat


def solve_dist_mat(residue_position_args):
    residue_a, all_residues = residue_position_args
    ret = list()
    for residue_b in all_residues:
        dists = scipy.spatial.distance.cdist(residue_a, residue_b)
        ret.append(np.min(dists))
    return ret
