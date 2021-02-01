#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd

# 全データを結合
path_to_file = 'path_to_file'
filename_to_save = 'alldata_merged'

list_df = []
for filename in list(sorted([i for i in os.listdir(path_to_file) if '.xlsx' in i])):
    filename_crop = filename[:-5] 
    df = pd.read_excel(os.path.join(path_to_file, filename))
    df.columns = ['基本目標と詳細', '基本的方向と詳細', '施策と詳細', '事業と詳細']
    df = df.dropna(axis=0, how='all').reset_index(drop=True) #空白行の削除
    df = df.fillna('') # 全セル内で一括で改行文字を削除するため, nanも空白の文字列に変換
    for i in df.columns:
        df[i] = df[i].str.replace('\n', '') # データ内の改行を削除
    
    df_cityname = pd.DataFrame([filename_crop.split(' ')]*len(df.index), columns=['No', '都道府県', '市区町村'])
    df = pd.concat([df_cityname, df], axis=1)
    list_df.append(df)

df_result = pd.concat(list_df, axis=0)
df_result.to_csv(os.path.join(path_to_file, filename_to_save+'.csv') , encoding='utf_8_sig', index=False)
del df_result

# 先ほど保存したファイルを読込, 自治体ごとに事業を###区切りのStringに変換('###nan'を発生させて文字列処理をするため)
df_merged = pd.read_csv(os.path.join(path_to_file, filename_to_save+'.csv'))
alldata = []
for cityno in df_merged['No'].unique():
    # 事業と詳細を###区切りのStringに変換
    jigyo = '事業'
    resultlist = []
    df_city = df_merged[df_merged['No']==cityno]
    
    for i in df_city['事業と詳細']:
        resultlist.append(str(i))
    resultstr = '###'.join(resultlist)
    resultstr = resultstr.replace('nan###', '')
    resultstr = resultstr.replace('###nan', '')
    
    # 事業と詳細が全て空白だった場合、施策と詳細を###区切りのStringに変換
    result_wonan = resultstr.replace('nan', '')
    result_wonan = result_wonan.replace('###', '')
    
    if len(result_wonan) == 0:
        jigyo = '施策'
        for i in df_city['施策と詳細']:
            resultlist.append(str(i))
        resultstr = '###'.join(resultlist)
        resultstr = resultstr.replace('nan###', '')
        resultstr = resultstr.replace('###nan', '')
        
    # 事業と詳細、施策と詳細が全て空白だった場合、基本的方向と詳細を###区切りのStringに変換
    result_wonan = resultstr.replace('nan', '')
    result_wonan = result_wonan.replace('###', '')
    
    if len(result_wonan) == 0:
        jigyo = '基本的方向'
        for i in df_city['基本的方向と詳細']:
            resultlist.append(str(i))
        resultstr = '###'.join(resultlist)
        resultstr = resultstr.replace('nan###', '')
        resultstr = resultstr.replace('###nan', '')
    
    citynames = list(df_city[['No',
                              '都道府県',
                              '市区町村']].loc[df_city.index[0]].values)
    
    resultstr = resultstr.replace(' ', '') # 半角スペース削除
    resultstr = resultstr.replace('　', '') # 全角スペース削除

    alldata.append(citynames + [jigyo, resultstr])

df_result = pd.DataFrame(alldata, columns=['No', '都道府県', '市区町村', '基本的方向/施策/事業', '詳細'])
df_result.to_csv(os.path.join(path_to_file, filename_to_save+'_onlyJigyo.csv'), index=False, encoding='utf_8_sig')