#! /usr/bin/env python
#################################################################################
#     File Name           :     ./gen_sub_ccmpred.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 19:32]
#     Last Modified       :     [2017-11-15 19:32]
#     Description         :      
#################################################################################
import numpy as np
with open("./tmp_feature/test.ccmpred") as fin:
    prediction = np.loadtxt(fin)

prediction = 0.5 * (prediction.T + prediction)
ret = []
for i in range(prediction.shape[0]):
    for j in range(i, prediction.shape[1]):
        ret.append((i + 1, j + 1, prediction[i][j]))


ret = sorted(ret, cmp=lambda x,y : -cmp(x[-1], y[-1]))
with open("./tmp_output/output_ccmpred.txt", "w") as fout:
    for i, j, k in ret[:50]:
        print >> fout, i, j, k



