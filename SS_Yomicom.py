
# coding: utf-8

# ## 作業内容
# - まとめサイトの総ページ取得
# - 全ページのURLをクロール

# In[336]:

## Library
from bs4 import BeautifulSoup
import urllib.request as req
import re,sys,time,datetime

import pandas as pd
import json

import os,shutil
import subprocess


# In[335]:

class SS_Yomicom:
    def __init__(self,url="http://yomicom.jp/"):
        self.url = url
        #src = self.getURL(url)

    # Yomicomのカテゴリ一覧/記事数/そのカテゴリのページ数を取得
    def Get_Category(self,output_file:".csv"):
        totalNum_pat = "\((.*)\)" #タイトル(数字)の数字部分だけ抽出
        #title_list=[] #jsonで書き出す用
        #カテゴリリストを書き出す
        src = self.getURL(self.url)
        categoryList_csv = open(output_file,"w")
        print("category_num,name,titleNum,page",file=categoryList_csv) #header
        for title in src.select("ul.main_menu > li > a"):
            totalNum = re.findall(totalNum_pat,title.text)[0] #総ページ数
            name = title.attrs["title"] #タイトル
            category_num = re.findall("\d+",title.attrs["href"])[0] #URLから数字だけ抽出
            #print("{}{}{}{}".format(category_num,name,totalNum,int(totalNum)//20),sep=",",file=categoryList_csv)
            print("{},{},{},{}".format(category_num,name,totalNum,int(totalNum)//20),file=categoryList_csv)
            #title_list.append({"category_num":category_num,"name":name,"totalNum":totalNum,"page":int(totalNum)//20})
        categoryList_csv.close()
        #return title_list

    #指定urlのhtmlソースを全て取得
    def getURL(self,url):
        res = req.urlopen(url)
        return BeautifulSoup(res,"html.parser")

    #指定url(まとめサイトの個別記事)のタイトル(スレタイ)を取得
    def getURL_title(self,url):
        src=getURL(url)
        title = src.select("div.ently_outline > h2.ently_title > a ")
        #re.search('title="(.*)"',title)
        title_pattern = ">(.*)</a>"
        title = str(title).replace("\n","")
        title = title.replace("\r","")
        try:
            title = re.findall(title_pattern,title,re.S)[0]
        except (ValueError,IndexError) as e:
            print("以下URLについて:",url)
            print("処理を中止します.\nエラー理由:",e)
            return
        return title

    #特定カテゴリの全ての個別記事のバックナンバーを取得し返す.
    #http://yomicom.jp/blog-category-33-"+str(page)+".html"
    def allPage_num(self,
                    category,
                    pages:int,
                    output_fileName):
        url="http://yomicom.jp/"
        category = "category-{}-".format(category)

        #SSの個別URLを記録する
        #ファイル名はカテゴリ名_list.txtにする.
        urlFile = open(output_fileName,"w")

        BackNumer_List=[] #そのカテゴリの個別記事のURLを記録
        for page in range(pages):
            _url = url+category+str(page)+".html"
            src = self.getURL(_url)
            #項目一覧取得
            pick= src.select("div.various_outline > div.various_body > div.various_text > ul > li > a")

            url_num = [] #BackNumberを一時的に記録する
            for i in pick:
                res=re.findall('#entry(.*)" ',str(i))
                url_num.append(res[0])

            for back_number in url_num:
                U = url +"blog-entry-"+back_number+".html"
                print(U,file=urlFile)
                BackNumer_List.append(U)

        urlFile.close()
        #return BackNumer_List

    ## URLを投げるとそのURL上のSS及びタイトルを取得してテキストで保存する
    def web_convert_text(self,
                         urlName:"SSのURLを投げて",
                         BN:"outputするテキストの名前"
                        ):
        src = self.getURL(urlName)
        #出力するファイル名はSSのタイトルにしました.(idの方が良いかもしれないけど)
        output_file = BN +".txt"

        text = src.select("div.ently_text > div.t_b")
        #div内のみ得る正規表現
        pat="<div class=\"t_b\">(.*)</div>"
        div_content = re.compile(pat,re.S)
        matome_list = []
        for line in text:
            #文字列に変換
            test = str(line)
            #<br/>を\nに変換
            test = test.replace("<br/>","\n")
            #print(test)
            test=div_content.findall(test)
            test.append("\n")
            matome_list.append(test)

        #リストを下げる
        flatten = lambda l: [item for sublist in l for item in sublist]
        res = flatten(matome_list)

        #まとめサイトのメインコンテンツをテキストで保存
        f = open(output_file,"w")
        for line in res:
            f.write(line)
        # print(self.getURL_title(urlName),file=f) #タイトルを保存する必要なくね
        #f.write("\n")
        f.write(urlName) #ソース書き込み

        #print("テキストに書き込みました.")
        f.close()
        return output_file

    #text -> json(キャラとその台詞を抽出する)
    def text_convert_json(self,
                          input_file:"txt",
                          output_file:"json"
                         ):
        #input_file = "test.txt" #変換元
        #output_file = "test.json" #変換先

        #ファイルの扱い
        with open(input_file) as f:
            text = f.read()
        output = open(output_file,"w")

        #パターン一覧
        chat_pattern = r"「(.+?)」"
        speaker_pattern = "(.*)(?=「)"
        #_chat_pattern = r"((.+?))"
        #_speaker_pattern = "(.*)(?=\()"

        text=re.sub(r"」(.+?)","」\n",text)

        json_dict=[]

        num=0 #台詞の順番を明記
        for i,line in enumerate(text.split("\n")):
            line = line.strip()
            if line=="":
                continue
            #print(i,"debug:",line)
            character = re.compile(speaker_pattern).findall(line)
            character_ = [c.strip() for c in character if c is not ""]
            #if character_ is '':
            #    continue
            #print(i,character_,line)
            speech = re.compile(chat_pattern,re.S).findall(line)
            if character_ ==[]:
                #print("-----------------")
                continue
            if len(character_[0]) >= 10:
                #print("-----------------")
                continue
            #print(i,character_,speech)
            json_dict.append({"id":num,"character":character_,"speech":speech})
            num+=1
            #print("-----------------")
        json.dump(json_dict,output,ensure_ascii=False,indent = 4,separators=(",",": "))
        #print("jsonに書き込みました")
        output.close()



# #### main文

# In[333]:

# Debug(Print文on) 他のloggerめんどくさい(´･ω･｀)てかどれいいかしらね.
def Debug_text_convert_json(input_file:"txt",output_file=None):
    #input_file = "test.txt" #変換元
    #output_file = "test.json" #変換先

    #ファイルの扱い
    with open(input_file) as f:
        text = f.read()
    #output = open(output_file,"w")

    #パターン一覧
    chat_pattern = r"「(.+?)」"
    speaker_pattern = "(.*)(?=「)"
    #_chat_pattern = r"((.+?))"
    #_speaker_pattern = "(.*)(?=\()"

    text=re.sub(r"」(.+?)","」\n",text)

    #json_dict=[]

    num=0 #台詞の順番を明記
    for i,line in enumerate(text.split("\n")):
        line = line.strip()
        if line=="":
            continue
        print(i,"debug:",line)
        character = re.compile(speaker_pattern).findall(line)
        character_ = [c.strip() for c in character if c is not ""]
        #if character_ is '':
        #    continue
        #print(i,character_,line)
        speech = re.compile(chat_pattern,re.S).findall(line)
        if character_ ==[]:
            print("-----------------")
            continue
        if len(character_[0]) >= 10:
            print("-----------------")
            continue
        print(i,character_,speech)
        #json_dict.append({"id":num,"character":character_,"speech":speech})
        num+=1
        print("-----------------")
        #json.dump(json_dict,output,ensure_ascii=False,indent = 4,separators=(",",": "))
        #print("jsonに書き込みました")
        #output.close()
