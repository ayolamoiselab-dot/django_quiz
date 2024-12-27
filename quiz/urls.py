from django.urls import path
from . import views

#URLconf
urlpatterns = [
    path('', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('post/', views.post, name='post'),
    path('contact/', views.contact, name='contact'),

]
 