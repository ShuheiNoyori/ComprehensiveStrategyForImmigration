#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer as FA
from matplotlib import pyplot as plt
plt.rcParams['font.family'] = 'Hiragino Sans'

##############################################
# Parameters
##############################################
n_factors = 10

##############################################
# Functions
##############################################
def FactorAnalysisFromDataFrame(df, n_factors):
    # データの標準化
    sc = StandardScaler()
    sc.fit(df)
    z = sc.transform(df)
    
    # 因子分析
    fa = FA(n_factors, rotation='oblimin')
    fa.fit(z)
    
    df_factor_score = pd.DataFrame(fa.transform(z), 
                                   columns = ['第{}因子'.format(i+1) for i in range(n_factors)], 
                                   index = [df.index])
    
    df_factor_loading = pd.DataFrame(fa.loadings_, 
                                     columns = ['第{}因子'.format(i+1) for i in range(n_factors)], 
                                     index = [df.columns])
    return df_factor_score, df_factor_loading

##############################################
# Main
##############################################
# データ読込
path_to_file = 'path_to_file'
filename = 'filename.csv' # 01_vectorize.py で出力したファイルの使用を想定

df = pd.read_csv(os.path.join(path_to_file, filename), index_col=0)

# 指定した因子数で因子分析
df_factor_score, df_factor_loading = FactorAnalysisFromDataFrame(df, n_factors)

# 因子負荷量が0.4未満の変数を消す
df_selected_factor_score, df_selected_factor_loading = df_factor_score, df_factor_loading
df_selected = df
selectedwords = [i[0] for i in  df_selected_factor_loading[df_selected_factor_loading>=0.4].dropna(how='all').index]

while len(selectedwords) < len(df_selected_factor_loading):
    df_selected = df[selectedwords]
    df_selected_factor_score, df_selected_factor_loading = FactorAnalysisFromDataFrame(df_selected, n_factors)
    selectedwords = [i[0] for i in  df_selected_factor_loading[df_selected_factor_loading>=0.4].dropna(how='all').index]
