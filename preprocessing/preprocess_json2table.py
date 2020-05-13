# -*- coding: utf-8 -*-
import json
import pandas as pd

##############################################
# Functions
##############################################
# 与えたdictのvalue（全階層）をlistにして返す
def dict2itemList(arg):
    result = []
    if isinstance(arg, str):
        result.append(arg)
    elif isinstance(arg, dict):
        for value in arg.values():
            result += dict2itemList(value)
    elif isinstance(arg, list):
        for item in arg:
            result += dict2itemList(item)
    return result

##############################################
# Main
##############################################

# データ読み込み
filename = 'ExcelFile_converted' # JSONファイル
json_file = open(filename + '.json', 'r')
json_load = json.load(json_file)
json_file.close()

# 全市町村のデータを取り出す （項目(item)ラベルなし）
itemlist = dict2itemList(json_load) # データの中身を全てlistとして取り出す
items_str = ', '.join(itemlist) # listの中身を全て、カンマ区切りでstrに変換

# 全市町村のデータを取り出す （項目(item)ラベルなし, 市町村ごと）
itemdict_city = {} # 市町村ごとの記載項目listのdict （key->市町村, value->記載項目list）
itemdict_city_str = {} # 市町村ごとの記載項目strのdict key->市町村, value->記載項目カンマ区切りstr）
for key in list(json_load.keys()):
    itemdict_city[key] = dict2itemList(json_load[key])
    itemdict_city_str[key] = ', '.join(dict2itemList(json_load[key]))

itemseries_city_str = pd.Series(itemdict_city_str) # 市町村ごとの記載項目strのdictをseriesに
itemseries_city_str.to_csv(filename + '_items.csv', encoding='cp932') # CSVに保存