from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .models import CategorieQuiz, Questionnaire

# Create your views here.

def home(request):
    return render(request, 'home/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

def category_list(request):
    categories = CategorieQuiz.objects.all()
    return render(request, 'categories/categorie.html', {'categories': categories})

def questionnaires_by_category(request, category_id):
    category = get_object_or_404(CategorieQuiz, id_cat=category_id)
    questionnaires = category.questionnaires.all()
    return render(request, "niveau/questionnaire.html", {
        "category": category,
        "questionnaires": questionnaires,
    })
    
def questions_by_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id_questionnaire=questionnaire_id)
    questions = questionnaire.questions.prefetch_related('choix').all()
    return render(request, "questions/questions.html", {
        "questionnaire": questionnaire,
        "questions": questions,
    })