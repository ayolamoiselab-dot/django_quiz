import json 
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .models import CategorieQuiz, Questionnaire, ResultatQuiz, Question, Choix
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import TemporaryCategoryForm
from .models import TemporaryCategory
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Exists, OuterRef
import json


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
    # Filtrer les catégories avec au moins un questionnaire associé
    categories = CategorieQuiz.objects.annotate(
        has_questionnaires=Exists(
            Questionnaire.objects.filter(categorie_id=OuterRef('id_cat'))
        )
    ).filter(has_questionnaires=True)  # On ne sélectionne que celles avec des questionnaires

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

@ensure_csrf_cookie  # Utilisation du bon décorateur
def save_answer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_id = data.get('question_id')
            answer = data.get('answer')
            
            # Stocker la réponse dans la session
            if question_id and answer:
                request.session[f'user_answer_{question_id}'] = answer
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def get_recap_data(questionnaire, session):
    recap_data = []
    for question in questionnaire.questions.all():
        user_answer = session.get(f'user_answer_{question.id_question}', 'Aucune réponse')
        correct_answer = question.choix.filter(est_correct=True).first()
        recap_data.append({
            'question': question,
            'user_answer': user_answer,
            'correct_answer': correct_answer.texte if correct_answer else "Aucune réponse",
            'is_correct': user_answer == (correct_answer.texte if correct_answer else None),
        })
    return recap_data


@login_required
def resultats_par_niveau(request, category_id, niveau):
    # Récupération de la catégorie
    categorie = get_object_or_404(CategorieQuiz, id_cat=category_id)

    # Vérification de l'existence d'un questionnaire pour le niveau actuel
    questionnaire = Questionnaire.objects.filter(categorie=categorie, niveau=niveau).first()
    if not questionnaire:
        messages.error(request, f"Aucun questionnaire trouvé pour la catégorie '{categorie.nom}' et le niveau '{niveau}'.")
        return redirect('category_list')

    # Calcul du score
    score = int(request.GET.get('score', 0))
    score_max = questionnaire.questions.count()

    if score_max == 0:
        messages.error(request, f"Le questionnaire pour le niveau '{niveau}' ne contient aucune question.")
        return redirect('category_list')

    pourcentage = (score / score_max) * 100

    # Récupération des réponses de l'utilisateur
    # recap_data = []
    # for question in questionnaire.questions.all():
    #     user_answer = request.session.get(f'user_answer_{question.id_question}', 'Aucune réponse')
    #     correct_answer = question.choix.filter(est_correct=True).first()
        
    #     recap_data.append({
    #         'question': question,
    #         'user_answer': user_answer,
    #         'correct_answer': correct_answer.texte if correct_answer else "Aucune réponse",
    #         'is_correct': user_answer == (correct_answer.texte if correct_answer else None)
    #     })

    recap_data = get_recap_data(questionnaire, request.session)

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
    try:
        index_niveau = niveaux.index(niveau)
    except ValueError:
        messages.error(request, f"Niveau '{niveau}' invalide.")
        return redirect('category_list')

    niveau_suivant = niveaux[index_niveau + 1] if index_niveau + 1 < len(niveaux) else None
    questionnaire_suivant = None

    if niveau_suivant:
        questionnaire_suivant = Questionnaire.objects.filter(categorie=categorie, niveau=niveau_suivant).first()

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
        'recap_data': recap_data,  # Ajouter les données du récapitulatif
    })





@login_required
def profile(request):
    user = request.user
    resultats_par_categorie = {}

    # Récupération des résultats de l'utilisateur par catégorie
    resultats = ResultatQuiz.objects.filter(user=user)
    
    # Calculer le nombre de demandes en attente de cet utilisateur
    demande_en_attente = TemporaryCategory.objects.filter(auteur=user, approuve=False).count()
    
    # Récupérer les catégories créées par l'utilisateur ou auxquelles il a participé
    categories_utilisateur = CategorieQuiz.objects.filter(auteur=user)


    # Organisation des résultats par catégorie et niveau
    for resultat in resultats:
        categorie = resultat.categorie
        niveau = resultat.niveau
        if categorie not in resultats_par_categorie:
            resultats_par_categorie[categorie] = {}
        if niveau not in resultats_par_categorie[categorie]:
            resultats_par_categorie[categorie][niveau] = []
        resultats_par_categorie[categorie][niveau].append(resultat)

    # Informations pour le profil
    total_quiz_joues = resultats.count()
    dernier_quiz = resultats.last()  # Dernier résultat basé sur la date de passage
    dernier_quiz_titre = dernier_quiz.categorie.titre if dernier_quiz else "Aucun"
    dernier_quiz_date = dernier_quiz.date_passage if dernier_quiz else None

    context = {
        'user': user,
        'resultats_par_categorie': resultats_par_categorie,
        'total_quiz_joues': total_quiz_joues,
        'dernier_quiz_titre': dernier_quiz_titre,
        'dernier_quiz_date': dernier_quiz_date,
        'demande_en_attente': demande_en_attente,
        'categories_utilisateur': categories_utilisateur,  # Passer les catégories auxquelles l'utilisateur est lié
    }

    return render(request, 'Profil/profil.html', context)


@login_required
def ajouter_quiz(request):
    if request.method == 'POST':
        form = TemporaryCategoryForm(request.POST)
        if form.is_valid():
            # Enregistrer la catégorie comme une proposition temporaire
            categorie = form.save(commit=False)
            categorie.auteur = request.user  # L'utilisateur connecté devient l'auteur
            categorie.save()
            # Ajouter un message de succès
            messages.success(request, "Demande Soumise !!!! En attente d'approbation...")
            return redirect('ajouter_quiz')  # Redirige vers une page de confirmation ou de liste des catégories

    else:
        form = TemporaryCategoryForm()

    return render(request, 'Ajout_Quiz/ajout_Quiz.html', {'form': form})



@csrf_exempt  # Ajouté pour permettre les requêtes POST avec un token CSRF
def ajouter_question(request):
    if request.method == 'POST':
        try:
            # Récupération des données envoyées par le formulaire
            data = json.loads(request.body)
            categorie_id = data['categorie_id']
            niveau_id = data['niveau_id']
            question_text = data['question_text']
            choices = data['choices']

            # Récupérer le questionnaire à partir de la catégorie et du niveau
            questionnaire = Questionnaire.objects.get(categorie_id=categorie_id, niveau=niveau_id)

            # Créer la question
            question = Question.objects.create(
                texte=question_text,
                questionnaire=questionnaire
            )

            # Créer les choix de réponse
            for choix in choices:
                Choix.objects.create(
                    texte=choix['text'],
                    est_correct=choix['isCorrect'],
                    question=question
                )

            # Retourner une réponse JSON de succès
            return JsonResponse({'success': True})

        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_niveaux(request, categorie_id):
    # Récupérer les niveaux distincts pour la catégorie donnée
    niveaux = Questionnaire.objects.filter(categorie_id=categorie_id).values('niveau').distinct()

    # Convertir les niveaux en liste de dictionnaires
    niveaux_list = [{"id": niveau['niveau'], "nom": niveau['niveau']} for niveau in niveaux]
    
    return JsonResponse({"niveaux": niveaux_list})


def apercu_questions(request, questionnaire_id):
    # Récupérer le questionnaire par ID
    questionnaire = get_object_or_404(Questionnaire, id_questionnaire=questionnaire_id)
    
    # Récupérer toutes les questions liées au questionnaire
    questions = questionnaire.questions.all()
    
    # Compter le nombre de questions
    
    nombre_questions = questions.count()
    
    # Passer les questions et le nombre de questions au template
    return render(request, 'niveau/aperçu_questions.html', {
        'questionnaire': questionnaire,
        'questions': questions,
        'nombre_questions': nombre_questions,
    })
