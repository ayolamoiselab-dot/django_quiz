from django.contrib import admin
from .models import (
    CategorieQuiz, Questionnaire, Question,
    Choix, UserProfil, ResultatQuiz, TemporaryCategory
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




# Configuration pour UserProfil
@admin.register(UserProfil)
class UserProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_joined')
    search_fields = ('user__username', 'user__email')


# Configuration pour ResultatQuiz
@admin.register(ResultatQuiz)
class ResultatQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'categorie', 'niveau', 'score', 'score_cat', 'termine', 'date_passage')  # Liste des champs à afficher
    search_fields = ('user__username', 'categorie__titre', 'niveau')  # Recherche dans les champs liés
    list_filter = ('niveau', 'categorie', 'termine')  # Filtrage selon certains champs

@admin.register(TemporaryCategory)
class TemporaryCategoryAdmin(admin.ModelAdmin):
    list_display = ('titre', 'niveau', 'nombre_questions', 'approuve', 'date_soumission')
    list_filter = ('approuve', 'niveau')
    actions = ['approuver_categories', 'refuser_categories', 'migrer_categories']

    def approuver_categories(self, request, queryset):
        """Action pour approuver les catégories sélectionnées"""
        queryset.update(approuve=True)

    def refuser_categories(self, request, queryset):
        """Action pour refuser les catégories sélectionnées"""
        queryset.delete()

    def migrer_categories(self, request, queryset):
        """Action pour migrer les données des catégories approuvées vers les autres tables"""
        for category in queryset:
            if category.approuve:
                # Migrer vers CategorieQuiz
                categorie_quiz = CategorieQuiz.objects.create(
                    titre=category.titre,
                    description=category.description,
                    auteur=category.auteur  # Assurez-vous que chaque catégorie a un utilisateur associé
                )

                # Migrer vers Questionnaire
                Questionnaire.objects.create(
                    categorie=categorie_quiz,  # CategorieQuiz devient l'ID de catégorie
                    niveau=category.niveau
                )

                # Optionnel : supprimez la catégorie temporaire après migration
                category.delete()

        self.message_user(request, "Les catégories ont été migrées avec succès!")

    migrer_categories.short_description = 'Migrer les catégories approuvées vers les tables appropriées'
    approuver_categories.short_description = 'Approuver les catégories sélectionnées'
    refuser_categories.short_description = 'Refuser les catégories sélectionnées'
#admin.site.register(TemporaryCategory, TemporaryCategoryAdmin)