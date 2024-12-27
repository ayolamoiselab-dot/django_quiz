from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.

def login(request):
    if request.method == 'POST':
        return redirect('index')
    return render(request, 'LoginPage/index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def index(request):
    return render(request, 'index.html')

def post(request):
    return render(request, 'post.html')
