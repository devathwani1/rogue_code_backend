from django.contrib import admin
from .models import Difficulty

@admin.register(Difficulty)
class DifficultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'days', 'number_of_questions')
