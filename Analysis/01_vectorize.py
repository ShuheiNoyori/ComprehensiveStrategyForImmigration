#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import MeCab
import unicodedata

##############################################
# Parameters
##############################################
global stopwords

part = '名詞'
excludelist = ['非自立', '代名詞', '接尾']
maxwords = 3000 # 解析対象の単語数. 出現回数上位maxwordsまでのものを解析.
colname = '詳細'
stopwords = ['事業', '課', 'H2', 'もの', 'ごと', 'ほか', 'それぞれ', 'および', 'もと',
             'ー', '一', '・'] # ストップワードのリスト
hiragana = [chr(0x3041 + i) for i in range(83)] # 平仮名1文字のリスト
katakana = [chr(0x30A1 + i) for i in range(86)] # 片仮名1文字のリスト
english_c = [chr(0xFF21 + i) for i in range(26)] # 英語大文字1文字のリスト
english_l = [chr(0xFF41 + i) for i in range(26)] # 英語小文字1文字のリスト
suji = [chr(0xADA1 + i) for i in range(30)] # 丸囲み数字, ローマ数字のリスト
stopwords += hiragana + katakana + english_c + english_l + suji

##############################################
# Functions
##############################################
def IsNumber(string): # 文字列が数値か判定
    try:
        float(string)
    except ValueError:
        return False
    else:
        return True

def Wakachi(text, part='名詞', excludelist=[]): #Stringを与えると指定した品詞のリストを返す
    tagger = MeCab.Tagger()
    tagger.parse('')
    node = tagger.parseToNode(unicodedata.normalize("NFKC", text))
    
    list_of_given_part = []
    while node:
        if node.feature.split(",")[0] == part: # 指定した品詞であるか
            if not node.feature.split(",")[1] in excludelist: # 除外する品詞分類を個別に指定
                word = node.surface
                if (not IsNumber(word)) and (not word in stopwords): #数字, ストップワードの場合はリストに入れない
                    list_of_given_part.append(word)
        node = node.next
    
    return list_of_given_part

def WakachiPerIndex(df, colname, part='名詞', excludelist=[]): # データフレームの指定した列について行ごとに分かち書きして, 指定した品詞のみpandas.Seriesで返す
    list_of_words_per_index = []
    for index in df.index:
        text_to_analyze = df[colname].iloc[index]
        list_of_words = Wakachi(text_to_analyze, part = part, excludelist = excludelist)
        list_of_words_per_index.append(list_of_words)
    
    return pd.Series(list_of_words_per_index, name = 'ListOfWords')

def FrequencyOfWords(series_part): # 単語リストのSeriesを与えると, 単語の出現回数をpandas.Seriesで返す
    list_of_words = []
    for i in series_part:
        list_of_words.extend(i)
        
    return pd.Series(list_of_words).value_counts()

def VectorizerBagOfWords(series_part, word_list): # 単語リストのSeriesとiterableな単語帳を与えるとBag of words(np.array)を返す
    vec_bin, vec_bow = [], []
    
    for index in series_part.index:
        list_of_words = series_part[index]
        index_vec_bin, index_vec_bow = [], []
        
        for word in word_list:
            
            if word in list_of_words:
                index_vec_bin.append(1)
            else:
                index_vec_bin.append(0)
                
            index_vec_bow.append(list_of_words.count(word))
            
        vec_bin.append(index_vec_bin)
        vec_bow.append(index_vec_bow)
    
    return np.array(vec_bin), np.array(vec_bow)

def VectorizerTfIdf(vec_binary, vec_bag_of_words): # VectorizerBagOfWordsの出力を与えるとtf-idf値のベクトルを返す(np.array)
    (size0, size1) = vec_binary.shape
    
    tf = vec_bag_of_words/(np.array(list(vec_bag_of_words.sum(axis = 1))*size1).reshape((size1, size0)).T)
    idf = np.log(size0/(np.array(list(vec_binary.sum(axis = 0))*size0).reshape((size0, size1))))
    
    tf_idf = tf*idf
    tf_idf_scale = tf_idf/(np.array(list(np.sqrt((tf_idf**2).sum(axis = 1)))*size1).reshape((size1, size0)).T)
    
    return tf_idf_scale

##############################################
# Main
##############################################
# データ読込
path_to_file = 'path_to_file'
filename = 'filename.csv'

df = pd.read_csv(os.path.join(path_to_file, filename))

series_noun = WakachiPerIndex(df, colname, part, excludelist) # 分かち書き
freq_noun = FrequencyOfWords(series_noun) # 単語の出現回数
freq_noun_analyze = freq_noun[:maxwords] # 解析対象の単語

# ベクトル化
vec_binary, vec_bag_of_words = VectorizerBagOfWords(series_noun, freq_noun_analyze.index)
vec_tf_idf = VectorizerTfIdf(vec_binary, vec_bag_of_words)

# デーダフレームとして保存
df_vec_bag_of_words = pd.DataFrame(vec_bag_of_words, 
                                   index = df[['No', '都道府県', '市区町村']],
                                   columns = freq_noun_analyze.index)
df_vec_bag_of_words.to_csv(os.path.join(path_to_file, 'bagOfWords_{}.csv'.format(maxwords)), 
                           encoding='utf-8-sig')

df_vec_tf_idf = pd.DataFrame(vec_tf_idf, 
                             index = df[['No', '都道府県', '市区町村']],
                             columns = freq_noun_analyze.index)
df_vec_tf_idf.to_csv(os.path.join(path_to_file, 'tfidf_{}.csv'.format(maxwords)), 
                     encoding='utf-8-sig')
