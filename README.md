# -ComprehensiveStrategyForImmigration
総合戦略のテキストデータ解析

前処理MergeData.pyで.xlsx形式の全自治体分のファイルを読み込み, 結合してます.

# 以下は古い情報ですが割と重要なこと書いてるのでそのまま残してます
## 対応するPythonスクリプト
- preprocess_excel2json.py
- preprocess_json2table.py

## 解析の環境
- Python 3.7.3 on Windows 10 (64-bit) ←Minicondaで入れた
- Mecabはここ( https://github.com/ikegami-yukino/mecab/releases/tag/v0.996 )のをダウンロードして使った 
- Anaconda Promptで`pip install mecab-python-windows`で無理矢理入れた

## データの構造
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
