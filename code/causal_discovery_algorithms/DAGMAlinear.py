import torch
from dagma import utils
from dagma.linear import DagmaLinear
from dagma.nonlinear import DagmaMLP, DagmaNonlinear
import pandas as pd
import numpy as np
import argparse
import os
import time
from scipy.stats import zscore

parser = argparse.ArgumentParser(
                    prog='DAGMA',
                    description='Generate adjacency matrix representing causal structure from scaled input',
                    epilog='Text at the bottom of help')

parser.add_argument('-i', '--inputPATH', type=str, help="input file location")
parser.add_argument('-o', '--outputPATH', type=str, help="output file location")
parser.add_argument("--lambda1", type=float, help="L1 regularization coefficient")
parser.add_argument('--w_threshold', type=float, default=0, help='Drop edge if |weight| < threshold')
parser.add_argument('--time_path', type=str, help="output time file")
parser.add_argument("--zscore", action = 'store_true', help = "z-score input data (i.e. set mean = 0, stdev = 1)")


args = parser.parse_args()

inputPATH = args.inputPATH
outputPATH = args.outputPATH
lambda1 = args.lambda1
time_path = args.time_path
w_threshold = args.w_threshold

df = pd.read_csv(inputPATH, sep="\t")   # read dummy .tsv file into memory

if (args.zscore):
    df = df.apply(zscore)

a = df.values


# get the start time
st = time.process_time()
st2 = time.time()

model = DagmaLinear(loss_type='l2') # create a linear model with least squares loss
W_est = model.fit(a, w_threshold = w_threshold,lambda1=lambda1) # fit the model with L1 reg. (coeff. 0.02)

ans = pd.DataFrame(W_est, columns = df.columns, index = df.columns)

# get cpu execution time
et = time.process_time()
res = et - st

# get total run time
et2 = time.time()
res2 = et2 - st2

ans.to_csv(outputPATH, sep="\t")

with open(time_path, 'w') as f:
    f.write('CPU Execution time: ' + str(res) + ' s' + '\n')
    f.write('runtime: ' + str(res2) + " s")
