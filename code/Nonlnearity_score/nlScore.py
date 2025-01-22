import numpy as np
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import pandas as pd
import matplotlib.pyplot as plt
from operator import truediv
import argparse
import os

parser = argparse.ArgumentParser(
                    prog='nlScore',
                    description='Generate adjacency matrix representing causal structure from scaled input',
                    epilog='Text at the bottom of help')

parser.add_argument('-i', '--inputPATH', type=str, help="input file location")
parser.add_argument('-o', '--outputPATH', type=str, help="output file location")
parser.add_argument('-n', '--nfeatures', type=int, help="numbers of features to select, n=5,10,15,20")
parser.add_argument('--fileName', type=str, help="output file name")

args = parser.parse_args()

inputPATH = args.inputPATH
outputPATH = args.outputPATH
fileName = args.fileName
num_features_to_select = args.nfeatures

# df = pd.read_csv("/home/yuehua/Projects/Causal_wTakis/sergio/input/"+str(dataset)+"/simulated_noNoise_T_"+str(simulation)+"_subgraph_"+str(subgraph)+"_subsample_1"+".tsv", sep="\t",index_col=0)   # read dummy .tsv file into memory
df = pd.read_csv(inputPATH, sep="\t",index_col=0)   # read dummy .tsv file into memory

X = df.values

selected_features = np.random.choice(X.shape[1], num_features_to_select, replace=False)

# Scale the entire dataset first
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Placeholder for storing results
results = []

for feature_idx in selected_features:
    # Define the dependent variable and independent variables
    y_target = X_scaled[:, feature_idx]
    X_independent = np.delete(X_scaled, feature_idx, axis=1)
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_independent, y_target, test_size=0.2, random_state=42)
    
    # Elastic Net setup
    elastic_net = ElasticNet()
    alphas = np.logspace(-4, 1, 50)  # Alpha ranges from 10^-4 to 10^1
    parameters_en = {'alpha': alphas, 'l1_ratio': [0.1, 0.5, 0.9]}
    grid_search_en = GridSearchCV(elastic_net, parameters_en, scoring='neg_mean_squared_error', cv=5)
    
    # XGBoost setup
    xgb = XGBRegressor()
    parameters_xgb = {'n_estimators': [50, 100, 200], 'max_depth': [3, 5, 7], 'learning_rate': [0.01, 0.1, 0.2]}
    grid_search_xgb = GridSearchCV(xgb, parameters_xgb, scoring='neg_mean_squared_error', cv=5)
    
    # Fit models
    grid_search_en.fit(X_train, y_train)
    grid_search_xgb.fit(X_train, y_train)
    
    # Evaluate models
    mse_en = mean_squared_error(y_test, grid_search_en.best_estimator_.predict(X_test))
    mse_xgb = mean_squared_error(y_test, grid_search_xgb.best_estimator_.predict(X_test))
    
    # Collect results
    results.append({
        'feature_index': feature_idx,
        'best_mse_elastic_net': mse_en,
        'best_params_elastic_net': grid_search_en.best_params_,
        'best_mse_xgboost': mse_xgb,
        'best_params_xgboost': grid_search_xgb.best_params_
    })

# Print or analyze results
with open(str(outputPATH)+'/'+str(fileName)+"_result.txt", 'w') as output:
    for result in results:
        output.write(str(result) + '\n')

data = results
# Extracting data
feature_indices = [item['feature_index'] for item in data]
best_mse_elastic_net = [item['best_mse_elastic_net'] for item in data]
best_mse_xgboost = [item['best_mse_xgboost'] for item in data]
nonlinear_score = list(map(truediv, best_mse_elastic_net, best_mse_xgboost))
with open(str(outputPATH)+'/'+str(fileName)+"_nonlinearScore.txt", 'w') as output:
    for res in nonlinear_score:
        output.write(str(res) + '\n')

# Plotting
fig, ax = plt.subplots()

bar_width = 0.35
index = range(len(feature_indices))

# Bars for elastic_net
bars1 = plt.bar(index, best_mse_elastic_net, bar_width, label='Elastic Net')

# Bars for xgboost
bars2 = plt.bar([i + bar_width for i in index], best_mse_xgboost, bar_width, label='XGBoost')

# Labels and title
plt.xlabel('Feature Index')
plt.ylabel('Best MSE')
plt.title('Best MSE by Feature Index and Model')
plt.xticks([i + bar_width / 2 for i in index], feature_indices)
plt.legend()

plt.tight_layout()
plt.show()
plt.savefig(str(outputPATH)+'/'+str(fileName)+'_nonlinearity.pdf')