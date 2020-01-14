
from django.urls import path
from . import views
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('recommend/', views.mysql_read_list, name='show_list'),
]