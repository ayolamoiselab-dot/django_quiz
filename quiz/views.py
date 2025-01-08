import json 
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .models import CategorieQuiz, Questionnaire, ResultatQuiz, Question, Choix
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


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


@login_required
def resultats_par_niveau(request, category_id, niveau):
    # Récupération de la catégorie
    categorie = get_object_or_404(CategorieQuiz, id_cat=category_id)

    # Vérification de l'existence d'un questionnaire pour ce niveau
    questionnaire = Questionnaire.objects.filter(categorie=categorie, niveau=niveau).first()
   

    # Récupération du score de la requête GET
    score = int(request.GET.get('score', 0))
    score_max = 100
    pourcentage = (score / score_max) * 100 if score_max > 0 else 0

    # Sauvegarde ou mise à jour du résultat
    user = request.user
    resultat, created = ResultatQuiz.objects.get_or_create(
        user=user,
        categorie=categorie,
        niveau=niveau,
        defaults={
            'score': pourcentage,
            'termine': True,
        }
    )
    if not created:
        resultat.score = pourcentage
        resultat.termine = True
        resultat.save() 

    # Détermination du niveau suivant
    niveaux = ['facile', 'intermediaire', 'avance']
    index_niveau = niveaux.index(questionnaire.niveau)
    niveau_suivant = niveaux[index_niveau + 1] if index_niveau + 1 < len(niveaux) else None

    if niveau_suivant:
        questionnaire_suivant = Questionnaire.objects.filter(categorie=categorie, niveau=niveau_suivant).first()
        if not questionnaire_suivant:
        # Si aucun questionnaire n'est trouvé pour ce niveau, vous pouvez gérer l'erreur
        # Par exemple, rediriger ou afficher un message d'erreur
            return redirect('category_list')  # Exemple de redirection
    else:
        questionnaire_suivant = None  # Pas de questionnaire pour le niveau suivant

   
    # Rendu du template
    return render(request, 'resultats/resultat.html', {
        'categorie': categorie,
        'niveau': niveau,
        'score': score,
        'score_max': score_max,
        'pourcentage': pourcentage,
        'niveau_suivant': niveau_suivant,
        'questionnaire': questionnaire,
        'questionnaire_suivant': questionnaire_suivant,

    })



@login_required
def profile(request):
    user = request.user
    resultats_par_categorie = {}

    # Exemple de récupération des résultats de l'utilisateur par catégorie
    resultats = ResultatQuiz.objects.filter(user=user)
    
    # Récupération des résultats par catégorie et niveau
    for resultat in resultats:
        categorie = resultat.categorie
        niveau = resultat.niveau
        if categorie not in resultats_par_categorie:
            resultats_par_categorie[categorie] = {}
        if niveau not in resultats_par_categorie[categorie]:
            resultats_par_categorie[categorie][niveau] = []
        resultats_par_categorie[categorie][niveau].append(resultat)
    
    # Autres informations pour le profil
    total_quiz_joues = resultats.count()
    dernier_quiz = resultats.last().categorie.titre if resultats else "Aucun"

    context = {
        'user': user,
        'resultats_par_categorie': resultats_par_categorie,
        'total_quiz_joues': total_quiz_joues,
        'dernier_quiz': dernier_quiz,
    }

    return render(request, 'Profil/profil.html', context)

@login_required
def ajouter_quiz(request):
    if request.method == 'POST':
        # Récupération des informations du formulaire
        titre_quiz = request.POST['quizTitle']
        description_quiz = request.POST['quizDescription']
        niveau_quiz = request.POST['quizLevel']
        nombre_questions = int(request.POST['quizQuestions'])
        categorie_quiz_id = request.POST['quizCategory']
        categorie_quiz = CategorieQuiz.objects.get(id_cat=categorie_quiz_id)

        # Création du questionnaire
        questionnaire = Questionnaire.objects.create(
            titre=titre_quiz,
            description=description_quiz,
            niveau=niveau_quiz,
            categorie=categorie_quiz,
            auteur=request.user.username
        )

        # Redirection après la création du quiz
        return redirect('quiz:category_list')  # Remplacez avec l'URL appropriée pour la liste des quiz

    # Récupérer les catégories et les niveaux du formulaire
    categories = CategorieQuiz.objects.all()
    niveaux = ['facile', 'intermediaire', 'avance']

    # Vérification des niveaux avant de les passer au template
    print("Niveaux disponibles : ", niveaux)

    return render(request, 'Ajout_Quiz/ajout_Quiz.html', {
        'categories': categories,
        'niveaux': niveaux
    })




