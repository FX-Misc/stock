#%%
import time
import math
import sys
import argparse
import cPickle as pickle

import numpy as np
from chainer import cuda, Variable, FunctionSet
import chainer.functions as F
from CharRNN import CharRNN, make_initial_state
import codecs

#%% arguments
parser = argparse.ArgumentParser()

parser.add_argument('--model',      type=str,   required=True)
parser.add_argument('--vocabulary', type=str,   required=True)

parser.add_argument('--seed',       type=int,   default=123)
parser.add_argument('--sample',     type=int,   default=1)
parser.add_argument('--primetext',  type=str,   default='')
parser.add_argument('--length',     type=int,   default=2000)
parser.add_argument('--gpu',        type=int,   default=-1)

args = parser.parse_args()

np.random.seed(args.seed)

# load vocabulary
vocab = pickle.load(open(args.vocabulary, 'rb'))
ivocab = {}
for c, i in vocab.items():
    ivocab[i] = c

# load model
model = pickle.load(open(args.model, 'rb'))
n_units = model.embed.W.shape[1]

if args.gpu >= 0:
    cuda.init()
    model.to_gpu()

# initialize generator
state = make_initial_state(n_units, batchsize=1, train=False)
if args.gpu >= 0:
    for key, value in state.items():
        value.data = cuda.to_gpu(value.data)

prev_char = np.array([0])
if args.gpu >= 0:
    prev_char = cuda.to_gpu(prev_char)

sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

if len(args.primetext) > 0:
    for i in unicode(args.primetext, 'utf-8'):
        sys.stdout.write(i)
        prev_char = np.ones((1,)).astype(np.int32) * vocab[i]
        if args.gpu >= 0:
            prev_char = cuda.to_gpu(prev_char)

        state, prob = model.predict(prev_char, state)

for i in xrange(args.length):
    state, prob = model.predict(prev_char, state)

    if args.sample > 0:
        probability = cuda.to_cpu(prob.data)[0].astype(np.float64)
        probability /= np.sum(probability)
        index = np.random.choice(range(len(probability)), p=probability)
    else:
        index = np.argmax(cuda.to_cpu(prob.data))
    sys.stdout.write(ivocab[index])

    prev_char = np.array([index])
    if args.gpu >= 0:
        prev_char = cuda.to_gpu(prev_char)

print
