import torch
from dagma import utils
from dagma.linear import DagmaLinear
from dagma.nonlinear import DagmaMLP, DagmaNonlinear
import pandas as pd
import numpy as np
import argparse
import os
import time
import sys
from scipy.stats import zscore

parser = argparse.ArgumentParser(
                    prog='DAGMAnonLinear',
                    description='Generate adjacency matrix representing causal structure from scaled input',
                    epilog='Text at the bottom of help')

parser.add_argument('-i', '--inputPATH', type=str, help="input file location")
parser.add_argument('-o', '--outputPATH', type=str, help="output file location")
parser.add_argument("--lambda1", type=float, help="L1 regularization coefficient")
parser.add_argument("--lambda2", type=float, help="L2 regularization coefficient")
parser.add_argument('--w_threshold', type=float, default=0, help='Drop edge if |weight| < threshold')
parser.add_argument('--time_path', type=str, help="output time file")
parser.add_argument("--zscore", action = 'store_true', help = "z-score input data (i.e. set mean = 0, stdev = 1)")



args = parser.parse_args()

inputPATH = args.inputPATH
outputPATH = args.outputPATH
lambda1 = args.lambda1
lambda2 = args.lambda2
time_path = args.time_path
w_threshold = args.w_threshold

df = pd.read_csv(inputPATH, sep="\t")   # read dummy .tsv file into memory

if (args.zscore):
    df = df.apply(zscore)

a = df.values

# get the start time
st = time.process_time()
st2 = time.time()

# note: using torch.double instead of torch.float gives better result for larger num of nodes
eq_model = DagmaMLP(dims=[a.shape[1], 10, 1], bias=True, dtype=torch.double) # create the model for the structural equations, in this case MLPs
model = DagmaNonlinear(eq_model, dtype=torch.double) # create the model for DAG learning
W_est_nonLinear = model.fit(a, lambda1=lambda1, lambda2=lambda2, w_threshold=w_threshold) # fit the model with L1 reg. (coeff. 0.01) and L2 reg. (coeff. 0.005)

ans = pd.DataFrame(W_est_nonLinear, columns = df.columns, index = df.columns)

# get the end time
et = time.process_time()
# get execution time
res = et - st

ans.to_csv(outputPATH, sep="\t")

et2 = time.time()
res2 = et2 - st2
with open(time_path, 'w') as f:
    f.write('CPU Execution time: ' + str(res) + ' s' + '\n')
    f.write('runtime: ' + str(res2) + " s")
