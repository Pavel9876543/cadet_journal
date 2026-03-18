"""
URL маршруты приложения journal.
"""

from django.urls import path
from . import views


urlpatterns = [

    # список оценок
    path("", views.grade_list, name="grade_list"),

    # журнал (главная страница)
    path("journal/", views.journal_table, name="journal_table"),

    # AJAX сохранение
    path("save-grade/", views.save_grade, name="save_grade"),

]