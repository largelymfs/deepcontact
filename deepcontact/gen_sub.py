#! /usr/bin/env python
#################################################################################
#     File Name           :     gen_sub.py
#     Created By          :     yang
#     Creation Date       :     [2017-11-15 19:28]
#     Last Modified       :     [2017-11-15 19:31]
#     Description         :      
#################################################################################
import cPickle

with open("./tmp_output/prediction.pkl", "rb") as fin:
    prediction = cPickle.load(fin)

prediction = 0.5 * (prediction.T + prediction)
ret = []
for i in range(prediction.shape[0]):
    for j in range(i, prediction.shape[1]):
        ret.append((i + 1, j + 1, prediction[i][j]))


ret = sorted(ret, cmp=lambda x,y : -cmp(x[-1], y[-1]))
with open("./tmp_output/output.txt", "w") as fout:
    for i, j, k in ret[:50]:
        print >> fout, i, j, k



