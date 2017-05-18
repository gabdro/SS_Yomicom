## Library
from bs4 import BeautifulSoup
import urllib.request as req
import re,sys,time,datetime

import pandas as pd
import json

import os,shutil
import subprocess

## crawling
from SS_Yomicom import *

import sys
argvs = sys.argv
argc = len(argvs)
if argc != 2:
    print("Usage # python {} AnimeTitle".format(argvs[0]))
    quit()

Chlor = SS_Yomicom()
Chlor.Get_Category("categoryList.csv") #カテゴリを取得 -> CategoryList.csvに出力
CategoryList = pd.read_csv("categoryList.csv") #先ほど取得したカテゴリ(csv)をpandasで表示
#CategoryList.columns #コラム取得

#任意のタイトルがリストに含まれているかどうかの確認
#anime_title="ガヴリールドロップアウト" #任意のタイトルでどうぞ
anime_title = argvs[1]
print("Research Title : {} ".format(anime_title))
Research_result = CategoryList[CategoryList["name"] == anime_title]
if len(Research_result)!=0:
    print(Research_result)
    category_num = int(Research_result["category_num"])
    page = int(Research_result["page"])
else:
    print("Not Found")
    quit()

# 非効率なので何か対処するかもしれない
output_fileName="getSS_list.txt"
#output_fileName = "gabdroSS_list.txt" #リストファイル
Chlor.allPage_num(category_num,page,output_fileName) #特定カテゴリの全ページの個別URLを記録

#一連の流れ
'''
sample_url="http://yomicom.jp/blog-entry-562.html"
bn = re.findall("\d+",sample_url)[0]
sample_text=Chlor.web_convert_text(sample_url,bn) #webのSSページ→テキストに書き込み
json_file = bn + ".json"
Chlor.text_convert_json(sample_text,json_file) #テキスト→json(キャラ/台詞)に書き込み
'''

## Debug(キャラ名「台詞」がうまく言っていなかった場合やおかしい点の確認)
'''
sample_text="562.txt"
Debug_text_convert_json(sample_text)
'''

## 実際に全てのSSをDLする場合にはallPage_num関数でカテゴリ内のリストをcsvで保存しておくこと
for i,line in enumerate(open(output_fileName,"r")):
    url=line.strip() #テキスト内の空白を削除
    #print(i,url)
    try:
        bn = re.findall("\d+",url)[0]
        text_file = Chlor.web_convert_text(url,bn) #web->text
        #sample_output="sample_json.json"
        json_file = bn + ".json" #URLの数字だけ抽出
        Chlor.text_convert_json(text_file,json_file) #text -> json
    except (ValueError,IndexError,FileNotFoundError) as e:
        print(e)

#.txt -> text / .json -> jsonに移動
if not os.path.isdir("txt"):
    os.mkdir("txt")
subprocess.call("mv *.txt txt/",shell=True)
if not os.path.isdir("JSON"):
    os.mkdir("JSON")
subprocess.call("mv *.json JSON/",shell=True)
