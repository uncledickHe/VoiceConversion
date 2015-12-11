#!/usr/bin/env python

import math
import numpy
import pickle
import sklearn
import sys

from evgmm import GMM

from stf import STF
from mfcc import MFCC
from dtw import DTW

D = 16

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print 'Usage: %s [gmmmap] [f0] [source speaker stf] (target speaker stf) [output]' % sys.argv[0]
        sys.exit()
    
    with open(sys.argv[1], 'rb') as infile:
        evgmm = pickle.load(infile)

    with open(sys.argv[2], 'rb') as infile:
        f0 = pickle.load(infile)

    source = STF()
    source.loadfile(sys.argv[3])

    mfcc = MFCC(source.SPEC.shape[1] * 2, source.frequency, dimension = D)
    source_mfcc = numpy.array([mfcc.mfcc(source.SPEC[frame]) for frame in xrange(source.SPEC.shape[0])])
    source_data = numpy.hstack([source_mfcc, mfcc.delta(source_mfcc)])

    if len(sys.argv) == 5:
        evgmm.fit(source_data)
    else:
        target = STF()
        target.loadfile(sys.argv[4])

        mfcc = MFCC(target.SPEC.shape[1] * 2, target.frequency, dimension = D)
        target_mfcc = numpy.array([mfcc.mfcc(target.SPEC[frame]) for frame in xrange(target.SPEC.shape[0])])
        target_data = numpy.hstack([target_mfcc, mfcc.delta(target_mfcc)])

        evgmm.fit(target_data)

    output_mfcc = evgmm.convert(source_data)
    output_spec = numpy.array([mfcc.imfcc(output_mfcc[frame]) for frame in xrange(output_mfcc.shape[0])])

    f0_data = []
    for i in source.F0:
        if i == 0:
            f0_data.append(i)
        else:
            f0_data.append(math.e ** ((math.log(i) - f0[0][0]) * f0[1][1] / f0[1][0] + f0[0][1]))

    source.SPEC = output_spec
    source.F0 = numpy.array(f0_data)

    if len(sys.argv) == 5:
        source.savefile(sys.argv[4])
    else:
        source.savefile(sys.argv[5])
