from django.db import models
from django.contrib.auth.models import User


# Modèle pour la catégorie de quiz
class CategorieQuiz(models.Model):
    id_cat = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    auteur = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=50, blank=True)  # Code de l'icône Font Awesome (e.g., "fa-user-alt")


    def __str__(self):
        return self.titre


# Modèle pour le questionnaire
class Questionnaire(models.Model):
    id_questionnaire = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255)
    categorie = models.ForeignKey(
        CategorieQuiz, on_delete=models.CASCADE, related_name="questionnaires"
    )
    niveau = models.CharField(
        max_length=50, 
        choices=[
            ('facile', 'Facile'),
            ('intermediaire', 'Intermédiaire'),
            ('avance', 'Avancé')
        ],
        default='facile'  # Par défaut, on commence avec "facile"
    )

    niveau_suivant = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='niveau_precedent'
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('titre', 'categorie', 'niveau')  # Contraintes d'unicité

    def __str__(self):
        return f"{self.titre} ({self.categorie.titre}, {self.niveau})"

   


# Modèle pour les questions
class Question(models.Model):
    id_question = models.AutoField(primary_key=True)
    texte = models.TextField()
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name="questions"
    )

    def __str__(self):
        return self.texte


# Modèle pour les choix de réponses
class Choix(models.Model):
    id_choix = models.AutoField(primary_key=True)
    texte = models.CharField(max_length=255)
    est_correct = models.BooleanField(default=False)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choix"
    )

    def __str__(self):
        return self.texte


# Modèle utilisateur personnalisé
# Modèle utilisateur (extension d'AbstractUser pour inclure plus de champs)
# class User(AbstractUser):
#     id_user = models.AutoField(primary_key=True)

#     # Ajoute des noms de relations inversées uniques pour éviter les conflits
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='custom_user_set',  # Nom de relation unique
#         blank=True,
#         help_text='The groups this user belongs to.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='custom_user_permissions_set',  # Nom de relation unique
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )


# Modèle pour le profil utilisateur
class UserProfil(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profil"
    )
    date_joined = models.DateTimeField(auto_now_add=True)


# Modèle pour les résultats des quiz
class ResultatQuiz(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="resultat_quiz"
    )
    categorie = models.ForeignKey(
        CategorieQuiz, on_delete=models.CASCADE, related_name="resultats"
    )
    niveau = models.CharField(
        max_length=50, 
        choices=[
            ('facile', 'Facile'),
            ('intermediaire', 'Intermédiaire'),
            ('avance', 'Avancé')
        ],
        default='facile'
    )
    score = models.FloatField()
    score_cat = models.FloatField(default=0)

    termine = models.BooleanField(default=False)
    
    date_passage = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'categorie', 'niveau', 'date_passage')  # Évite les doublons de résultats

    def __str__(self):
        return f"{self.user.username} - {self.categorie.titre} ({self.niveau})  {self.score_cat}%"