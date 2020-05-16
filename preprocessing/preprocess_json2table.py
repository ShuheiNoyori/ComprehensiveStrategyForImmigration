# -*- coding: utf-8 -*-
import json
import pandas as pd

##############################################
# Functions
##############################################
# 与えたdictのvalue（全階層）をlistにして返す -nanも含めたリストで返す
def dict2itemList(arg):
    result = []
    if isinstance(arg, dict):
        for value in arg.values():
            result += dict2itemList(value)
    elif isinstance(arg, list):
        for item in arg:
            result += dict2itemList(item)
    elif isinstance(arg, str) or isinstance(arg, float):
        result.append(str(arg))
    return result

# 与えたdictのkey（全階層）をlistにして返す　※その階層のkeyのみ
# ちゃんと動くが無駄な部分がある気がする
def dict2keyList(arg):
    result = []
    if isinstance(arg, dict):
        for key, value in arg.items():
            if isinstance(value, str) or isinstance(value, float):
                result.append(key)
            else:
                result += dict2keyList(value)
    elif isinstance(arg, list):
        for item in arg:
            result += dict2keyList(item)
    else:
        result.append(arg)
    return result

def dict2dataframe(arg):
    city_list, item_list, key_list = [], [], []
    for key in list(json_load.keys()):
        # 全自治体のデータを取り出す （項目(item)ラベルなし）
        item_list_i = dict2itemList(arg[key]) # データの中身を全てlistとして取り出してlistに追加
        item_list.extend(item_list_i) # 後の方でlistの長さを使うので変数を作っています
        # 全自治体のデータから項目(item)ラベルのみを取り出す
        key_list.extend(dict2keyList(arg[key])) # データのkeyを全てlistとして取り出してlistに追加
        # 都市名リスト
        city_list.extend([key]*len(item_list_i))
        
    df_item = pd.DataFrame([city_list, key_list, item_list]).T
    df_item.columns = ['自治体名', '項目', '項目内容']
    return df_item
    
##############################################
# Main
##############################################

# データ読み込み
filename = 'ExcelFile_converted' # JSONファイル
json_file = open(filename + '.json', 'r')
json_load = json.load(json_file)
json_file.close()

# 全自治体のデータを取り出す （項目(item)ラベルなし, 自治体ごと）
itemdict_city = {} # 自治体ごとの記載項目listのdict （key->自治体, value->記載項目list）
itemdict_city_str = {} # 自治体ごとの記載項目strのdict key->自治体, value->記載項目カンマ区切りstr）
for key in list(json_load.keys()):
    itemdict_city[key] = dict2itemList(json_load[key])
    itemdict_city_str[key] = ', '.join(dict2itemList(json_load[key]))

itemseries_city_str = pd.Series(itemdict_city_str) # 自治体ごとの記載項目strのdictをseriesに
itemseries_city_str.to_csv(filename + '_items_str.csv', encoding='cp932') # CSVに保存

df_items = dict2dataframe(json_load)
df_items.to_csv(filename + '_items.csv', encoding='cp932', index=None) # CSVに保存
