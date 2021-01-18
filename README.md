# -ComprehensiveStrategyForImmigration
総合戦略のテキストデータ解析
## 解析環境
https://qiita.com/paulxll/items/72a2bea9b1d1486ca751 を参考に設定  
- macOS Catalina 10.15.7  
- Python 3.7.9 (Anacondaで仮想環境"MeCab"を作ってそこに設定)
- MeCab 0.996
- 辞書 NEologd (デフォルトで使用する辞書をこちらに設定)

## 0. 前処理
[MergeData.py](https://github.com/ShuheiNoyori/ComprehensiveStrategyForImmigration/blob/master/preprocessing/MergeData.py)で.xlsx形式の全自治体分のファイルを読み込み結合.
- alldata_merged.csv: データの結合のみ. 改行は削除.
- alldata_merged_onlyjigyo.csv: 1自治体を1行にデータの形を変換. 事業の間は###で区切った. 事業がない場合は施策, 施策もない場合は基本的方向を事業の代わりとした.  
  
## 1. 解析  
### 1-1. データのベクトル化
[01_vectorize.py](https://github.com/ShuheiNoyori/ComprehensiveStrategyForImmigration/blob/master/Analysis/01_vectorize.py)で, alldata_merged_onlyjigyo.csvを読み込みベクトル化したデータをcsv形式で保存. 解析対象の単語は出現回数上位{maxwords}までのものとして指定. 
- bagOfWords_{maxwords}.csv: 単語の出現頻度のベクトル  
- tfidf_{maxwords}.csv: tf-idf値のベクトル  
  
### 1-2. ワードクラウド描画  
[02_wordcloud.py](https://github.com/ShuheiNoyori/ComprehensiveStrategyForImmigration/blob/master/Analysis/02_wordcloud.py)で, bagOfWords_{maxwords}.csvまたはtfidf_{maxwords}.csvを読み込んでワードクラウドを描画. 市区町村コードで描画する市区町村を指定する.
- wordcloudでの日本語フォントの表示はhttps://openbook4.me/sections/1674 を参考に設定した.  
- 頻度データからのワードクラウド描画はhttps://analytics-note.xyz/programming/frequencies-word-cloud/ を参考にした.  

## 以下は古い情報ですが割と重要なこと書いてるのでそのまま残してます
#### 対応するPythonスクリプト
```
preprocess_excel2json.py
preprocess_json2table.py
```  

#### 解析の環境
- Python 3.7.3 on Windows 10 (64-bit) ←Minicondaで入れた
- Mecabはここ( https://github.com/ikegami-yukino/mecab/releases/tag/v0.996 )のをダウンロードして使った 
- Anaconda Promptで`pip install mecab-python-windows`で無理矢理入れた

#### データの構造
- 総合戦略の項目は「基本目標」「基本的方向」「施策」「事業」の4レイヤーからなるツリー構造を取っている
- また, 各項目は"項目", "項目詳細", "項目KPI"からなる 
以上から, JSONデータの構造は下記のとおり 
  
```
{  
    "自治体名": [  
        {  
            "基本目標": "...",  
            "基本目標詳細": "...",  
            "基本目標KPI": "...",  
            "基本的方向リスト": [  
                {  
                    "基本的方向": "...",  
                    "基本的方向詳細": "...",  
                    "基本的方向KPI": "...",  
                    "施策リスト": [  
                        {  
                            "施策": "...",  
                            "施策詳細": "...",  
                            "施策KPI": "...",  
                            "事業リスト": [  
                                {  
                                    "事業": "...",  
                                    "事業詳細": "...",  
                                    "事業KPI": "..."  
                                },  
                                {  
                                    "事業": "...",  
                                    "事業詳細": "...",  
                                    "事業KPI": "..."  
                                },  
                                ...  
                            ]  
                        },  
                        ...  
                    ]  
                },  
                ...  
            ]  
        },  
        ...  
    ],  
    ...  
}  
