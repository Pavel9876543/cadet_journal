"""
Формы приложения.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from journal.models import Subject, Cadet


# =========================
# ФОРМА ЛОГИНА
# =========================

class LoginForm(AuthenticationForm):
    """
    Форма авторизации пользователя.
    """

    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Введите логин"
        })
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Введите пароль"
        })
    )


# =========================
# ФОРМА ВЫСТАВЛЕНИЯ ОЦЕНКИ
# =========================

class GradeForm(forms.Form):
    """
    Форма для выставления оценки (ручной ввод).
    """

    cadet = forms.ModelChoiceField(
        queryset=Cadet.objects.all(),
        label="Курсант",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label="Предмет",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    value = forms.CharField(
        label="Оценка",
        max_length=10,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Например: 5, 4-, н"
        })
    )


# =========================
# ФОРМА ЭКЗАМЕН / ИТОГ
# =========================

class SubjectResultForm(forms.Form):
    """
    Форма для экзамена и итоговой оценки.
    """

    cadet = forms.ModelChoiceField(
        queryset=Cadet.objects.all(),
        label="Курсант",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label="Предмет",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    exam = forms.CharField(
        required=False,
        max_length=10,
        label="Экзамен",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Экзамен"
        })
    )

    final = forms.CharField(
        required=False,
        max_length=10,
        label="Итог",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Итог"
        })
    )