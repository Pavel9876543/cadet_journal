
from django.urls import path
from . import views

urlpatterns=[
path('',views.grade_list,name="grade_list"),
path('journal/',views.journal_table,name="journal"),
path('save_journal/',views.save_journal,name="save_journal"),
]
