import pandas as pd
import numpy as np
import argparse
import os
import time
import cdt
import networkx as nx
from scipy.stats import zscore

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
human_readable = lambda delta: ['%d %s' % (getattr(delta, attr), attr if getattr(delta, attr) > 1 else attr[:-1])
    for attr in attrs if getattr(delta, attr)]

from cdt.causality.graph import PC

parser = argparse.ArgumentParser(
                    prog='cdt_kpc',
                    description='Generate adjacency matrix representing causal structure from scaled input',
                    epilog='Text at the bottom of help')

parser.add_argument('-i', '--inputPATH', type=str, help="input file location")
parser.add_argument('-o', '--outputPATH', type=str, help="output file location")
parser.add_argument('--time_path', type=str, help="output time file")
parser.add_argument("--alpha", type=float, help="L1 regularization coefficient")
parser.add_argument("--CItest", type=str, help="CItest, rcit or rcot")
parser.add_argument("--zscore", action = 'store_true', help = "z-score input data (i.e. set mean = 0, stdev = 1)")


args = parser.parse_args()

inputPATH = args.inputPATH
outputPATH = args.outputPATH
alpha = args.alpha
CItest = args.CItest
time_path = args.time_path

df = pd.read_csv(inputPATH, sep="\t")   # read dummy .tsv file into memory

if (args.zscore):
    df = df.apply(zscore)

# get the start time (python)
st = time.process_time()
st2 = time.time()
# get start time (global)
st_gp_times = os.times()

# run PC
pc_output = PC(CItest=CItest, alpha=alpha).create_graph_from_data(df)

# save result as adj matrix
ans = pd.DataFrame(nx.adjacency_matrix(pc_output).todense(), columns = df.columns, index = df.columns)

# get cpu execution time (python)
et = time.process_time()
res = et - st

ans.to_csv(outputPATH, sep="\t")

# get total run time (python)
et2 = time.time()
res2 = et2 - st2
# get end time (global)
end_gp_times = os.times()

with open(time_path, 'w') as f:
    f.write('CPU Execution time: ' + str(res) + ' s' + '\n')
    f.write('runtime: ' + str(res2) + " s" + '\n')
    f.write('os.time start: ' + str(st_gp_times) + '\n')
    f.write('os.time end: ' + str(end_gp_times) + '\n')
    f.write('os.time end-start: ' + str(tuple(np.subtract(end_gp_times, st_gp_times))))
