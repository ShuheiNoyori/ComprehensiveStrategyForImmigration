#### Python3.7以降で動かしてください ###
# ∵Python3.7から、dictがOrderedDictと同じ挙動をするようになったことを利用している
import pandas as pd
import numpy as np
import json

def ItemCategorize(length, category_exists, item_dict): # itemをcategoryの下に仕分ける
    category_index0 = list(np.where(category_exists)[0]) # categoryの下にあるitem開始のインデックス
    category_index1 = list(np.where(category_exists)[0])[1:] + [length]    # categoryの下にあるitem終了のインデックス
    item_list_level_category = []
    for ci0, ci1 in zip(category_index0, category_index1):
        item_list_level_category.append([item_dict[key] for key in item_dict.keys() if ci0<=key and key<ci1]) # categoryレベルで分類したitemをリストとして保持
    return item_list_level_category

def Excel2Dict(df_sheets, key):
    df = df_sheets[key]
    length = len(df.index)
    for col in df.columns:
        # 姑息的にエラー吐く文字を消している
        df[col] = df[col].str.replace('\n', '') # 全ての改行文字を削除
        df[col] = df[col].str.replace('\u2248', '') # 無理矢理消した 
        df[col] = df[col].str.replace('\u5c10', '') # 無理矢理消した
    # 以下、ツリー構造の一番下から、事業→施策→基本的方針→基本目標の順に辿ってデータ作成する
    # 各項目が設定されている行のフラグを作成
    mokuhyo_exists = np.logical_not(np.logical_and(pd.isnull(df['基本目標']), pd.isnull(df['基本目標詳細'])))   # 基本目標が設定されている行のフラグ
    hoko_exists = np.logical_not(np.logical_and(pd.isnull(df['基本的方向']), pd.isnull(df['基本的方向詳細'])))    # 基本的方向が設定されている行のフラグ
    shisaku_exists = np.logical_not(np.logical_and(pd.isnull(df['施策']), pd.isnull(df['施策詳細'])))       # 施策が設定されている行のフラグ
    
    # 全項目のリストを作成. 各項目はdict形式{'項目':項目, '項目詳細':項目詳細, '項目KPI':項目KPI}
    mokuhyo_dict_ori = df[['基本目標', '基本目標詳細', '基本目標KPI']][mokuhyo_exists].T.to_dict()
    hoko_dict_ori = df[['基本的方向', '基本的方向詳細', '基本的方向KPI']][hoko_exists].T.to_dict()
    shisaku_dict_ori = df[['施策', '施策詳細', '施策KPI']][shisaku_exists].T.to_dict()
    jigyo_dict_ori = df[['事業', '事業詳細', '事業KPI']].T.to_dict()
        
    # 施策単位で事業を仕分ける ##########################################
    shisaku_dict_result = {}
    if shisaku_exists.sum() > 0: # 施策が1件以上設定されている場合
        jigyo_list_shisakuLevel = ItemCategorize(length, shisaku_exists, jigyo_dict_ori) # 施策レベルにまとまった事業のリスト
        for num, shisaku, jigyo_shisakuLevel in zip(list(shisaku_dict_ori.keys()), list(shisaku_dict_ori.values()), jigyo_list_shisakuLevel):
            shisaku['事業リスト'] = jigyo_shisakuLevel
            shisaku_dict_result[num] = shisaku
    else: # 施策が設定されていない場合→基本的方向1つに対して1つ施策が想定されているものと考える
        if hoko_exists.sum() > 0: # 基本的方向が1件以上設定されている場合
            jigyo_list_shisakuLevel = ItemCategorize(length, hoko_exists, jigyo_dict_ori) # 基本的方向レベルにまとまった事業のリスト
            for num, jigyo_shisakuLevel in zip(list(hoko_dict_ori.keys()), jigyo_list_shisakuLevel):
                shisaku_dict_result[num] = {'施策':np.nan, '施策詳細':np.nan, '施策KPI':np.nan, '事業リスト':jigyo_shisakuLevel}
                
        # ここの処理にバグあるかも（該当するデータがなくて確認できてない） #####
        else: # 基本的方向も設定されていない場合→基本目標1つに対して1つ施策が想定されているものと考える
            if mokuhyo_exists.sum() > 0: # 基本目標が1件以上設定されている場合
                jigyo_list_shisakuLevel = ItemCategorize(length, mokuhyo_exists, jigyo_dict_ori) # 基本的方向レベルにまとまった事業のリスト
                for num, jigyo_shisakuLevel in zip(list(mokuhyo_dict_ori.keys()), jigyo_list_shisakuLevel):
                    shisaku_dict_result[num] = {'施策':np.nan, '施策詳細':np.nan, '施策KPI':np.nan, '事業リスト':jigyo_shisakuLevel}
            else:
                print(key) # 基本目標がないのはどう見てもおかしいのでエラー
                return([])
        # ここまで #####
    
    # 基本的方向単位で施策を仕分ける ##########################################
    hoko_dict_result = {}
    if hoko_exists.sum() > 0: # 基本的方向が1件以上設定されている場合
        shisaku_list_hokoLevel = ItemCategorize(length, hoko_exists, shisaku_dict_result)
        for num, hoko, shisaku_hokoLevel in zip(list(hoko_dict_ori.keys()), list(hoko_dict_ori.values()), shisaku_list_hokoLevel):
            hoko['施策リスト'] = shisaku_hokoLevel
            hoko_dict_result[num] = hoko
    else: # 基本的方向が設定されていない場合→基本目標1つに対して1つ基本的方向が想定されているものと考える
        if mokuhyo_exists.sum() > 0: # 基本目標が1件以上設定されている場合
            shisaku_list_hokoLevel = ItemCategorize(length, mokuhyo_exists, shisaku_dict_result)
            for num, shisaku_hokoLevel in zip(list(mokuhyo_dict_ori.keys()), shisaku_list_hokoLevel):
                hoko_dict_result[num] = {'基本的方向':np.nan, '基本的方向詳細':np.nan, '基本的方向KPI':np.nan, '施策リスト':shisaku_hokoLevel}
        else:
            print(key) # 基本目標がないのはどう見てもおかしいのでエラー
            return([])
        
    # 基本目標単位で基本的方向を仕分ける ##########################################
    mokuhyo_dict_result = {}
    if mokuhyo_exists.sum() > 0: # 基本目標が1件以上設定されている場合
        hoko_list_mokuhyoLevel = ItemCategorize(length, mokuhyo_exists, hoko_dict_result)
        for num, mokuhyo, hoko_mokuhyoLevel in zip(list(mokuhyo_dict_ori.keys()), list(mokuhyo_dict_ori.values()), hoko_list_mokuhyoLevel):
            mokuhyo['基本的方向リスト'] = hoko_mokuhyoLevel
            mokuhyo_dict_result[num] = mokuhyo
    else:
        print(key) # 基本目標がないのはどう見てもおかしいのでエラー
        return([])
    return(mokuhyo_dict_result)

##################################
# Main
##################################
df_sheets = pd.read_excel('ExcelFile.xlsx', sheet_name=None, skiprows=1, dtype=str)
data_senryaku = {}
for key in df_sheets: # sheet毎にデータを取り出して処理
    data_senryaku[key] = Excel2Dict(df_sheets, key)
    
with open('ExcelFile_converted.json', 'w') as f:
    json.dump(data_senryaku, f, indent=4, ensure_ascii=False)
