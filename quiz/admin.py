from django.contrib import admin
from .models import (
    CategorieQuiz, Questionnaire, Question,
    Choix, User, UserProfil, ResultatQuiz
)

# Configuration pour CategorieQuiz
@admin.register(CategorieQuiz)
class CategorieQuizAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_creation')
    search_fields = ('titre', 'auteur')
    list_filter = ('date_creation',)


# Configuration pour Questionnaire
@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'date_creation', 'update')
    search_fields = ('titre',)
    list_filter = ('categorie', 'date_creation', 'update')


# Inline pour Choix dans Question
class ChoixInline(admin.TabularInline):
    model = Choix
    extra = 3  # Nombre de champs de choix vides par défaut


# Configuration pour Question
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('texte', 'questionnaire')
    search_fields = ('texte',)
    list_filter = ('questionnaire__categorie', 'questionnaire')
    inlines = [ChoixInline]


# Configuration pour Choix
@admin.register(Choix)
class ChoixAdmin(admin.ModelAdmin):
    list_display = ('texte', 'question', 'est_correct')
    list_filter = ('question__questionnaire',)
    search_fields = ('texte',)


# Configuration pour User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')


# Configuration pour UserProfil
@admin.register(UserProfil)
class UserProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_joined')
    search_fields = ('user__username', 'user__email')


# Configuration pour ResultatQuiz
@admin.register(ResultatQuiz)
class ResultatQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'categorie', 'score', 'date_passage')
    search_fields = ('user__username', 'categorie__titre')
    list_filter = ('date_passage', 'categorie')
