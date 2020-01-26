
from django.urls import path
from . import views
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('recommend/lfhdja', views.read_vec50, name='vec50'),
    path('recommend/khfajgd', views.read_vec60, name='vec60'),
]