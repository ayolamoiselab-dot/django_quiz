from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,name='home'),  # Route par défaut
    #path('home/', views.home), 
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/', views.category_list, name='category_list'),
    path("categories/<int:category_id>/questionnaires/", views.questionnaires_by_category, name="questionnaires_by_category"),
    path("questionnaires/<int:questionnaire_id>/questions/", views.questions_by_questionnaire, name="questions_by_questionnaire"),

]