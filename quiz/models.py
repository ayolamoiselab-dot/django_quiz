from django.contrib.auth.models import AbstractUser
from django.db import models



# Create your models here.

# Modèle pour la catégorie de quiz
class CategorieQuiz(models.Model):
    id_cat = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    auteur = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)

    def ajouter_questionnaire(self):
        pass  # A complèter

    def supprimer_questionnaire(self):
        pass  # A complèter

    def modifier_questionnaire(self):
        pass  # A complèter

    def obtenir_resultat(self):
        pass  # A complèter

# Modèle pour le questionnaire
class Questionnaire(models.Model):
    id_questionnaire = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    categorie = models.ForeignKey(CategorieQuiz, on_delete=models.CASCADE, related_name="questionnaires")

    def ajouter_question(self):
        pass  # A complèter

    def supprimer_question(self):
        pass  # A complèter

    def modifier_questionnaire(self):
        pass  # A complèter

# Modèle pour les questions
class Question(models.Model):
    id_question = models.AutoField(primary_key=True)
    texte = models.TextField()
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name="questions")

    def ajouter_choix(self):
        pass  # A complèter
    def definir_reponse_correcte(self):
        pass  # A complèter

    def obtenir_choix(self):
        pass  # A complèter

# Modèle pour les choix de réponses
class Choix(models.Model):
    id_choix = models.AutoField(primary_key=True)
    texte = models.CharField(max_length=255)
    est_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choix")

    def est_correct(self):
        return self.est_correct

# Modèle utilisateur (extension d'AbstractUser pour inclure plus de champs)
class User(AbstractUser):
    id_user = models.AutoField(primary_key=True)

    # Ajoute des noms de relations inversées uniques pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
# Modèle pour le profil utilisateur
class UserProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil")
    date_joined = models.DateTimeField(auto_now_add=True)

    def get_quiz_results(self):
        return self.user.resultat_quiz.all()

    def get_progress(self):
        pass  # A complèter

# Modèle pour les résultats des quiz
class ResultatQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resultat_quiz")
    categorie = models.ForeignKey(CategorieQuiz, on_delete=models.CASCADE, related_name="resultats")
    score = models.FloatField()
    date_passage = models.DateTimeField(auto_now_add=True)

    def calculer_score(self):
        pass  # A complèter

    def obtenir_statistique(self):
        pass  # A complèter
