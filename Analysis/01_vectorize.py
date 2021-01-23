#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import MeCab
import unicodedata
from matplotlib import pyplot as plt
plt.rcParams['font.family'] = 'Hiragino Sans'

##############################################
# Parameters
##############################################
global stopwords
global path_to_file

part = '名詞'
excludelist = ['非自立', '代名詞', '接尾', '形容動詞語幹']
maxwords = 3000 # 解析対象の単語数. 出現回数上位maxwordsまでのものを解析.
colname = '詳細'
stopwords_kobetsu = ['事業', 'もの', 'ほか', 'それぞれ', 'および', 'もと', 'ー', '一', '・',
                     '市', '本市', '市民', '市内', '区', '本区', '区民', '区内', 
                     '町', '本町', '町民', '町内', '村', '本村', '村民', '村内', ] # ストップワードのリスト
hiragana = [chr(0x3041 + i) for i in range(83)] # 平仮名1文字のリスト
katakana = [chr(0x30A1 + i) for i in range(86)] # 片仮名1文字のリスト
english_c = [chr(0xFF21 + i) for i in range(26)] # 英語大文字1文字のリスト
english_l = [chr(0xFF41 + i) for i in range(26)] # 英語小文字1文字のリスト
stopwords = stopwords_kobetsu + hiragana + katakana + english_c + english_l

##############################################
# Functions
##############################################
def IsNumber(string): # 文字列が数字か判定
    try:
        float(string)
    except ValueError:
        return False
    else:
        return True

def Wakachi(text, part='名詞', excludelist=[]): #Stringを与えると指定した品詞のリストを返す
    tagger = MeCab.Tagger()
    tagger.parse('')
    text = unicodedata.normalize('NFKC', text) # Unicode正規化
    node = tagger.parseToNode(text)
    
    list_of_given_part = []
    while node:
        if node.feature.split(",")[0] == part: # 指定した品詞であるか
            if not node.feature.split(",")[1] in excludelist: # 除外する品詞分類を個別に指定
                word = node.surface
                if (not IsNumber(word)) and \
                    (not word in stopwords): #数字, ストップワードの場合はリストに入れない
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

def FrequencyOfWords(series_part): # 単語リストのSeriesを与えると, 各単語の出現回数をpandas.Seriesで返す
    list_of_words = []
    for i in series_part:
        list_of_words.extend(i)
        
    return pd.Series(list_of_words).value_counts()

def WordCount(series_part): # 文章ごとの単語リストのSeriesを与えると, 文章ごとの単語数を返す
    list_of_word_count = []    
    for i in series_part:
        list_of_word_count.append(len(i))
        
    return pd.Series(list_of_word_count)

def WordCountHist(series_word_count): # 文章ごとの単語数のSeriesを与えるとヒストグラムを描画する
    plt.figure(figsize=(10, 6))
    plt.hist(series_word_count, bins = 50)
    plt.xlabel('文章内の単語数')
    plt.ylabel('頻度 (地方公共団体数)')
    plt.savefig(os.path.join(path_to_file, '地方公共団体ごとの文章内の単語数.png'), dpi = 400)

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
    idf = np.log(size0/(np.array(list(vec_binary.sum(axis = 0))*size0).reshape((size0, size1)) + 1)) + 1
    
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

series_word_count = WordCount(series_noun) # 文章ごとの単語数
series_word_count.index = df[['No', '都道府県', '市区町村']] # indexを市区町村名に変更
series_word_count.to_csv(os.path.join(path_to_file, 'wordcount_percity.csv'), encoding='utf-8-sig') #保存
WordCountHist(series_word_count)

freq_noun = FrequencyOfWords(series_noun) # 単語の出現回数
freq_noun_analyze = freq_noun[:maxwords] # 解析対象の単語

print('文章に含まれる単語のうち, {}のみを解析対象とした. また, {}のうち, {}と判定されたものは除外した. さらに頻出の単語である「事業」を除外したうえで, 出現頻度上位{:,}までの単語をベクトルの計算に用いた.'\
      .format(part,
              part,
              ', '.join(excludelist),
              maxwords))
print('出現した全{:,}種類の{}の出現頻度は全体で{:,}回であり, そのうち解析対象となったものは{:,}回, 全体の{:.02f}%であった.'\
      .format(len(freq_noun.index), 
              part, 
              freq_noun.sum(),
              freq_noun_analyze.sum(),
              100*freq_noun_analyze.sum()/freq_noun.sum()))

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
