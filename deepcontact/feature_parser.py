#! /usr/bin/env python
#################################################################################
#     File Name           :     feature_gen.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 16:59]
#     Last Modified       :     [2017-11-15 19:48]
#     Description         :      
#################################################################################
DTYPE = 'float32'
import os,sys
import numpy as np

def normalize(data):
    '''
        common data normalizer
    '''
    mean = np.mean(data)
    std = np.std(data)
    data -= mean
    if std != 0:
        data /= std
    return data

def normalize_zero_omitting(data):
    '''
        ignore all negative value
    '''
    data = normalize(data)
    data = np.maximum(0, data)
    return data

############2d-feature parsers ##############
def ccmpred_parser_2d(filename, max_len):
   buf = np.zeros((1, max_len, max_len), dtype = DTYPE)
   try:
       data = np.loadtxt(filename)
   except:
       return None
   data = normalize(data)
   leng, _ = data.shape
   assert(leng <= max_len)
   buf[0, :leng, :leng] = data[:, :]
   return buf

def ccmpred_parser_2d_zero(filename, max_len):
   buf = np.zeros((1, max_len, max_len), dtype = DTYPE)
   try:
       data = np.loadtxt(filename)
   except:
       return None
   data = normalize_zero_omitting(data)
   leng, _ = data.shape
   assert(leng <= max_len)
   buf[0, :leng, :leng] = data[:, :]
   return buf

def pairstats_parser_2d(filename, max_len):
    buf = np.zeros((3, max_len, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return None
    with open(filename) as fin:
        for l in fin:
            words = l.strip().split()
            x, y, a, b, c = words
            x = int(x) - 1
            y = int(y) - 1
            a = float(a)
            b = float(b)
            c = float(c)
            buf[0, x, y] = a
            buf[0, y, x] = a
            buf[1, x, y] = b
            buf[1, y, x] = b
            buf[2, x, y] = c
            buf[2, y, x] = c
    return buf

def evfold_parser_2d(filename, max_len):
    buf = np.zeros((1, max_len, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return None
    with open(filename) as fin:
        for l in fin:
            words = l.strip().split()
            x = int(words[0]) - 1
            y = int(words[2]) - 1
            a = float(words[-1])
            buf[0, x, y] = a
            buf[0, y, x] = a
    buf = normalize(buf)
    return buf

def evfold_parser_2d_zero(filename, max_len):
    buf = np.zeros((1, max_len, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return None
    with open(filename) as fin:
        for l in fin:
            words = l.strip().split()
            x = int(words[0]) - 1
            y = int(words[2]) - 1
            a = float(words[-1])
            buf[0, x, y] = a
            buf[0, y, x] = a
    buf = normalize_zero_omitting(buf)
    return buf

def ss2_parser_1d(filename, max_len):
    buf = np.zeros((3, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return None
    index = 0
    with open(filename) as fin:
        for l in fin:
            words = l.strip().split()
            if len(words) !=6:
                continue
            buf[0][index] = float(words[3])
            buf[1][index] = float(words[4])
            buf[2][index] = float(words[5])
            index += 1
    return buf

def solv_parser_1d(filename, max_len):
    buf = np.zeros((1, max_len), dtype=DTYPE)
    if not os.path.isfile(filename):
        return None
    index = 0
    with open(filename) as fin:
        for l in fin:
            words = l.strip().split()
            if len(words)!= 3:
                continue
            buf[0][index] = float(words[2])
            index += 1
    return buf

def colstats_parser_1d(filename, max_len):
    buf = np.zeros((22, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return None
    index = 0
    with open(filename) as fin:
        for l in fin:
            words = l.strip().split()
            if len(words) != 22:
                continue
            words = np.array([float(item) for item in words], dtype=DTYPE)
            buf[:,index] = np.reshape(words, (22, 1))[:,0]
            index += 1
    return buf

def neff_parser_1d(filename, max_len):
    buf = np.zeros((1, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return buf
    try:
        with open(filename) as fin:
            for _ in xrange(4):
                line = fin.readline()
            while not line.startswith("Effective number of sequences exp(entropy)"):
                line = fin.readline()
                if not line:
                    break
            neff = float(line.strip().split()[-1])
            sys.stdout.flush()
    except:
        neff = 0
    buf[0, :] = neff
    return buf

def ccmpred_std_parser_1d(filename, max_len):
    buf = np.zeros((1, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return buf
    with open(filename) as fin:
        data = np.loadtxt(filename)
        std = np.std(data)
    buf[0, :] = std
    return buf

def evfold_std_parser_1d(filename, max_len):
    tmp_buf = np.zeros((1, max_len, max_len), dtype = DTYPE)
    buf = np.zeros((1, max_len), dtype = DTYPE)
    if not os.path.isfile(filename):
        return None
    with open(filename) as fin:
        for l in fin:
            words = l.strip().split()
            x = int(words[0]) - 1
            y = int(words[2]) - 1
            a = float(words[-1])
            tmp_buf[0, x, y] = a
            tmp_buf[0, y, x] = a
        std = np.std(tmp_buf)
    buf[0, :] = std
    return buf

function_map = {
    'ccmpred_parser_2d' :   ccmpred_parser_2d,
    'ss2_parser_1d'     :   ss2_parser_1d,
    'solv_parser_1d'    :   solv_parser_1d,
    'pairstats_parser_2d':  pairstats_parser_2d,
    'colstats_parser_1d':   colstats_parser_1d,
    'evfold_parser_2d'  : evfold_parser_2d,
    'neff_parser_1d' : neff_parser_1d,
    'ccmpred_std_parser_1d' : ccmpred_std_parser_1d,
    'evfold_std_parser_1d' : evfold_std_parser_1d,
    'evfold_parser_2d_zero':evfold_parser_2d_zero,
    'ccmpred_parser_2d_zero':ccmpred_parser_2d_zero,
}
