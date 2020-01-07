from django.shortcuts import render
from django.utils import timezone
from .models import Post
from .models import RawFromApi
from urllib import request as ureq
from bs4 import BeautifulSoup

# Create your views here.

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def mysql_read_list(request):
    likes_count=100
    user_likes_url="https://qiita.com/toutou/like"
    try:
        likes_count=request.POST['likes_count']
        user_likes_url = str(request.POST['url'])
    except (KeyError):
        pass
    
    
    #get html
    html = ureq.urlopen(user_likes_url)
    
    #set BueatifulSoup
    soup = BeautifulSoup(html, "html.parser")
    atags=soup.find_all("a", attrs={"class", "u-link-no-underline"})
    url_title_id_list = list()
    for atag in atags:
        url='https://qiita.com'+str(atag.get('href'))
        splited_url=url.split('/')
        article_id = splited_url[-1]
        url_title_id_list.append([url,atag.string,article_id])

    #rows = RawFromApi.objects.using('mysql').filter(likes_count__gte=likes_count)
    rows = RawFromApi.objects.using('mysql').filter(likes_count=likes_count)
    count =len(rows)
    return render(request,'blog/show_rows.html',
    {'rows':rows,'likes_count':likes_count,'request':request,
    'count':count,'url_list':url_title_id_list,'user_likes_url':user_likes_url})
   
def mysql_seach(request):
    rows = RawFromApi.objects.using('mysql').get(id=3)
    return render(request,'blog/show_rows.html',{'rows':rows})