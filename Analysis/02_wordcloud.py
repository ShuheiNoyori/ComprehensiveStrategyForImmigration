#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
from matplotlib import pyplot as plt
plt.rcParams['font.family'] = 'Hiragino Sans'
import wordcloud

##############################################
# Parameters
##############################################
citycode = 1100

##############################################
# Functions
##############################################
def CityCode2Index(df, citycode=1100): # 市区町村コードからdfに対応するindexを返す. 指定がない場合は1100北海道札幌市.
    list_city_code = [int(i[1:i.index(',')]) for i in df.index]
    if citycode in list_city_code:
        return df.index[list_city_code.index(citycode)]

def Dict2WordCloud(dictofwordsandvalues, figtitle=''): # {単語: 任意の指標} の形で作成されたdictのデータからword cloudを描画
    wc = wordcloud.WordCloud(font_path='/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc',
                             width=600,
                             height=400,
                             prefer_horizontal=1,
                             background_color='white',
                             include_numbers=True
                             ).generate_from_frequencies(dictofwordsandvalues)
    
    plt.figure()
    plt.axis('off')
    if figtitle!='':
        plt.title(figtitle)
    plt.imshow(wc)
    
def WordCloud(df, citycode=1100): #市区町村コードで指定した市区町村のワードクラウドを出力. 指定がない場合は1100北海道札幌市.
    index = CityCode2Index(df, citycode) # 市区町村コードで市区町村を指定
    print(index)
    dict_words = df.loc[index].to_dict() # 指定された市区町村のデータをdictに変換
    dict_words = {k: v for k, v in dict_words.items() if v > 0} # tf-idf値が正のもののみ残す
    Dict2WordCloud(dict_words, index)

##############################################
# Main
##############################################
# データ読込
path_to_file = 'path_to_file'
filename = 'filename.csv' # 01_vectorize.py で出力したファイルの使用を想定

df = pd.read_csv(os.path.join(path_to_file, filename), index_col=0)

# ワードクラウド描画
WordCloud(df, citycode)