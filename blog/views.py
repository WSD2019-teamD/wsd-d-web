from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Post
from .models import RawFromApi
from urllib import request as ureq
from bs4 import BeautifulSoup
import json
import datetime




# Create your views here.

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def mysql_read_list(request):
    likes_count=100
    user_likes_url=""
    try:
        # likes_count=request.POST['likes_count']
        user_likes_url = str(request.POST['url'])
    except (KeyError):
        pass
    
    if(user_likes_url=="") :
        return render(request,'blog/show_rows.html',
    {'request':request,'url_list':[],'user_likes_url':""})
    
    #get html
    html = ureq.urlopen(user_likes_url)
    
    #set BueatifulSoup
    soup = BeautifulSoup(html, "html.parser")
    atags=soup.find_all("a", attrs={"class", "u-link-no-underline"})
    url_title_id_list = list()
    user_article_id = list()
    for atag in atags:
        url='https://qiita.com'+str(atag.get('href'))
        splited_url=url.split('/')
        article_id = splited_url[-1]
        url_title_id_list.append([url,atag.string,article_id])
        user_article_id.append(article_id)

    dict_similar_articles = dict()
    for url_title_id in url_title_id_list: 
        article_id=url_title_id[2]
        record = RawFromApi.objects.using('mysql').filter(article_id=article_id).first()
        if record == None:
            #record dose not exist on qiita_db
            continue
        
        #辞書の追加（既存のキーはアップデートされる）
        dict_similar_articles.update(json.loads(record.similar_articles)) 

    #推薦リストからいいね履歴を削除
    dict_similar_articles=drop_key(user_article_id,dict_similar_articles)
   
    #推薦記事をソートして、article_idのリストを返す(templateにdict_similar_articlesとrecommend_article_idsを渡す)
    all_recommend_articles = sort_articles(dict_similar_articles)
    paginator = Paginator(all_recommend_articles, 20) # 1ページに20件表示
    p = request.POST['button'] # URLのパラメータから現在のページ番号を取得
    print(p)
    recommend_articles = paginator.get_page(p) # 指定のページのArticleを取得
 
    return render(request,'blog/show_rows.html',
    {'request':request,'url_list':url_title_id_list,'user_likes_url':user_likes_url,
    'recommend_articles':recommend_articles})
   
def mysql_seach(request):
    rows = RawFromApi.objects.using('mysql').get(id=3)
    return render(request,'blog/show_rows.html',{'rows':rows})

def drop_key(key_list,dic):

    for key in key_list:
        value=dic.pop(key,None)
     
    return dic

def sort_articles(dic):
    #辞書からidと類似度のリストのリストを作りsortしたリストを返す
    #下のはイメージで書いてる
    simi = 1
    cre = 1
    like = 1
    articleId_scores = []
    for key,value in dic.items():
        today=datetime.datetime.today()
        created_at = datetime.datetime.strptime(value['created_at'], '%Y-%m-%d %H:%M:%S')
        td = abs(today -created_at)
     
        score =  200*float(value['similarities']) + float(value['likes_count'])/5 - td.days/100
        articleId_scores.append([key,score])

    articleId_scores.sort(key=lambda x: x[1],reverse=True)

    recommend_articles=list()
    for articleId_score in articleId_scores:
        recommend_articles.append(dic[articleId_score[0]])

    return  recommend_articles


    # article_ids = list(dic.keys())
    # print(article_ids)
    # return article_ids
