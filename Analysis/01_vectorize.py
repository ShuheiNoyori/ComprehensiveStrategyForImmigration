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
maxwords = 1000 # 解析対象の単語数. 出現回数上位maxwordsまでのものを解析.
colname = '詳細'
stopwords_kobetsu = ['事業', 'もの', 'ほか', 'それぞれ', 'および', 'もと', 'ー', '一', '・',
                     '市', '本市', '市民', '市内', '当市', '区', '本区', '区民', '区内', '当区', 
                     '町', '本町', '町民', '町内', '当町', '村', '本村', '村民', '村内', '当村'] # ストップワードのリスト
hiragana = [chr(0x3041 + i) for i in range(83)] # 平仮名1文字のリスト
katakana = [chr(0x30A1 + i) for i in range(86)] # 片仮名1文字のリスト
english_c = [chr(0xFF21 + i) for i in range(26)] # 英語大文字1文字のリスト
english_l = [chr(0xFF41 + i) for i in range(26)] # 英語小文字1文字のリスト
onebyte = [chr(0x0000 + i) for i in range(112)] # 1byte文字のリスト
stopwords = stopwords_kobetsu + hiragana + katakana + english_c + english_l + onebyte

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

def WakachiWithYomi(text, part='名詞', excludelist=[]): #Stringを与えると指定した品詞の単語と読みのリストを返す
    tagger = MeCab.Tagger()
    tagger.parse('')
    text = unicodedata.normalize('NFKC', text) # Unicode正規化
    node = tagger.parseToNode(text)
    
    list_of_given_part = []
    while node:
        if node.feature.split(",")[0] == part: # 指定した品詞であるか
            if not node.feature.split(",")[1] in excludelist: # 除外する品詞分類を個別に指定
                word = node.surface # 単語
                if (not IsNumber(word)) and \
                    (not word in stopwords): #数字, ストップワードの場合はリストに入れない
                    if len(node.feature.split(",")) > 7: # Featureに読みが含まれている場合は読みをリストに追加
                        yomi = node.feature.split(",")[7] # 読み
                    else: # Featureに読みが含まれていない場合は単語自体を読みとしてリストに追加
                        yomi = word
                    list_of_given_part.append([word, yomi])
        node = node.next
    
    return list_of_given_part

def WakachiPerIndexWithYomi(df, colname, part='名詞', excludelist=[]): # データフレームの指定した列について行ごとに分かち書きして, 指定した品詞のみpandas.Seriesで返す
    list_of_words_per_index = []
    for index in df.index:
        text_to_analyze = df[colname].iloc[index]
        list_of_words = WakachiWithYomi(text_to_analyze, part = part, excludelist = excludelist)
        list_of_words_per_index.append(list_of_words)
    
    return pd.Series(list_of_words_per_index, name = 'ListOfWords')

def StandardizeSpellingInconsistencies(series_part): # 表記揺れの標準化のためのCSVを書き出し
    list_of_words = []
    for i in series_part:
        list_of_words.extend(i)
        
    df_word_yomi = pd.DataFrame(list_of_words, columns = ['Word', 'Yomi']) # 単語と読みのDataFrame
    df_word_yomi = df_word_yomi.drop_duplicates(subset=['Word'], keep='first') # 同一の単語を削除
    list_same_yomi = []
    for yomi in df_word_yomi['Yomi'].unique():
        same_yomi = df_word_yomi[df_word_yomi['Yomi'] == yomi]['Word'].values.tolist()
        if len(same_yomi) > 1:
            list_same_yomi.append(','.join(same_yomi))
    pd.DataFrame(list_same_yomi, columns=['Words']).\
        to_csv('spelling_inconsistencies.csv', encoding='utf-8-sig', index=False)
        
def SpellingStandardizationDict(df_spelling_standardization): # DataFrameから表記揺れ標準化の辞書を作成
    list_keys, list_vals = [], []
    for words in df_spelling_standardization['Words']:
        list_words = words.split(',')
        
        list_keys += list_words
        list_vals += [list_words[0]]*len(list_words)
    
    dict_spelling_standardization = dict(zip(list_keys, list_vals))
    return dict_spelling_standardization

def Wakachi(text, part='名詞', excludelist=[]): #Stringを与えると指定した品詞の単語のリストを返す
    tagger = MeCab.Tagger()
    tagger.parse('')
    text = unicodedata.normalize('NFKC', text) # Unicode正規化
    node = tagger.parseToNode(text)
    
    list_of_given_part = []          
    while node:
        if node.feature.split(",")[0] == part: # 指定した品詞であるか
            if not node.feature.split(",")[1] in excludelist: # 除外する品詞分類を個別に指定
                word = node.surface # 単語
                if (not IsNumber(word)) and (not word in stopwords): #数字, ストップワードの場合はリストに入れない
                    list_of_given_part.append(word)
        node = node.next
    
    return list_of_given_part

def WakachiPerIndex(df, colname, part='名詞', excludelist=[]): # データフレームの指定した列について行ごとに分かち書きして, 指定した品詞のみpandas.Seriesで返す
    list_of_words_per_index = []
    for index in df.index:
        text_to_analyze = df[colname].iloc[index]
        list_of_words = Wakachi(text_to_analyze,
                                part = part,
                                excludelist = excludelist)
        list_of_words_per_index.append(list_of_words)
    
    return pd.Series(list_of_words_per_index, name = 'ListOfWords')

def FrequencyOfWords(series_part, dict_spelling_standardization = {}): # 単語リストのSeriesを与えると, 各単語の出現回数をpandas.Seriesで返す
    list_of_words = []
    for i in series_part:
        list_of_words.extend(i)
        
    if not dict_spelling_standardization == {}:
        list_of_words = [dict_spelling_standardization[word] \
                         if word in dict_spelling_standardization.keys() \
                         else word
                         for word in list_of_words]
        
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

# この部分は表記揺れの辞書作成のためだけに使用（同音異義語を出力し, それを人力で修正した辞書を読み込むことで表記揺れを標準化する）
# series_noun_yomi = WakachiPerIndexWithYomi(df, colname, part, excludelist) # 分かち書き（単語と読みの入ったpandas.Series）
# StandardizeSpellingInconsistencies(series_noun_yomi) # 表記揺れの標準化のためのCSVを書き出し
# ここまで

df_spelling_standardization = pd.read_csv('spelling_inconsistencies_selected.csv') # 表記揺れの標準化のためのCSVを編集したものを読み込み
dict_spelling_standardization = SpellingStandardizationDict(df_spelling_standardization) #DataFramaをdictに変換

series_noun = WakachiPerIndex(df, colname, part, excludelist) # 分かち書き（単語の入ったpandas.Series）
series_word_count = WordCount(series_noun) # 文章ごとの単語数
series_word_count.index = df[['No', '都道府県', '市区町村']] # indexを市区町村名に変更
WordCountHist(series_word_count)

freq_noun = FrequencyOfWords(series_noun, dict_spelling_standardization) # 単語の出現回数をカウント. 表記揺れの標準化も同時に行っている.
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
series_word_count.to_csv(os.path.join(path_to_file, 'wordcount_percity.csv'), encoding='utf-8-sig')

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
