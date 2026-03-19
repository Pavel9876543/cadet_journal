"""
Views приложения (тонкий слой).
"""

import json
from json import JSONDecodeError

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError

from journal.forms import LoginForm, GradeForm, SubjectResultForm
from journal.utils.roles import get_user_role, Role
from journal.utils.decorators import role_required

from journal.services.journal_service import get_journal_data
from journal.services.grade_service import set_grade, set_subject_result
from journal.services.attendance_service import get_attendance_data
from journal.services.grade_service import calculate_average_for_cadet_subject
from journal.models import SubjectResult, SubjectGroup


# =========================
# АВТОРИЗАЦИЯ
# =========================

def login_view(request):
    """
    Авторизация пользователя.
    """

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("dashboard")

    return render(request, "journal/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# DASHBOARD (РОЛИ)
# =========================

@login_required
def dashboard(request):
    """
    Перенаправление в зависимости от роли.
    """

    role = get_user_role(request.user)

    if role == Role.STUDENT:
        return redirect("student_dashboard")

    if role == Role.TEACHER:
        return redirect("teacher_dashboard")

    if role == Role.ADMIN:
        return redirect("journal")

    return redirect("login")


# =========================
# СТУДЕНТ
# =========================

@login_required
@role_required([Role.STUDENT])
def student_dashboard(request):

    cadet = request.user.cadet

    subjects = cadet.group.group_subjects.select_related("subject")

    averages = {}
    results = {}

    for sg in subjects:
        subject = sg.subject

        averages[subject.id] = calculate_average_for_cadet_subject(cadet, subject)

        res = SubjectResult.objects.filter(
            cadet=cadet,
            subject=subject
        ).first()

        results[subject.id] = {
            "exam": res.exam if res else None,
            "final": res.final if res else None
        }

    attendance = get_attendance_data(request.user)

    return render(request, "journal/student_dashboard.html", {
        "cadet": cadet,
        "averages": averages,
        "results": results,
        "attendance": attendance
    })


@login_required
@role_required([Role.TEACHER])
def teacher_dashboard(request):

    teacher = request.user.teacher

    subject_groups = SubjectGroup.objects.filter(
        teacher=teacher
    ).select_related("subject", "group")

    attendance = get_attendance_data(request.user)

    return render(request, "journal/teacher_dashboard.html", {
        "teacher": teacher,
        "subject_groups": subject_groups,
        "attendance": attendance
    })


# =========================
# ЖУРНАЛ
# =========================

@login_required
@role_required([Role.ADMIN, Role.TEACHER])
def journal_table(request):
    """
    Журнал оценок.
    """

    data = get_journal_data(
        user=request.user,
        group_id=request.GET.get("group"),
        subject_id=request.GET.get("subject"),
    )

    return render(request, "journal/journal_table.html", data)


# =========================
# СОХРАНЕНИЕ ОЦЕНКИ (AJAX)
# =========================

@login_required
@require_POST
def save_grade(request):
    """
    Сохранение оценки.
    """

    try:
        data = json.loads(request.body)

        cadet_id = data.get("cadet_id")
        lesson_id = data.get("lesson_id")
        value = data.get("value")

        if cadet_id is not None:
            cadet_id = int(cadet_id)

        if lesson_id is not None:
            lesson_id = int(lesson_id)

        if value is not None:
            value = int(value)

        set_grade(
            user=request.user,
            cadet_id=cadet_id,
            lesson_id=lesson_id,
            value=value,
        )

        return JsonResponse({"status": "ok"})

    except (JSONDecodeError, TypeError, ValueError):
        return JsonResponse({"error": "Неверный формат данных"}, status=400)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception:
        return JsonResponse({"error": "Ошибка сервера"}, status=500)


# =========================
# ЭКЗАМЕН / ИТОГ (AJAX)
# =========================

@login_required
@require_POST
def set_result(request):
    """
    Установка экзамена и итоговой оценки.
    """

    try:
        data = json.loads(request.body)

        cadet_id = data.get("cadet_id")
        subject_id = data.get("subject_id")
        value = data.get("value")

        if cadet_id is not None:
            cadet_id = int(cadet_id)

        if subject_id is not None:
            subject_id = int(subject_id)

        if value is not None:
            value = int(value)

        kwargs = {
            "user": request.user,
            "cadet_id": cadet_id,
            "subject_id": subject_id,
        }

        if data.get("type") == "exam":
            kwargs["exam"] = value
        else:
            kwargs["final"] = value

        set_subject_result(**kwargs)

        return JsonResponse({"status": "ok"})

    except (JSONDecodeError, TypeError, ValueError):
        return JsonResponse({"error": "Неверный формат данных"}, status=400)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception:
        return JsonResponse({"error": "Ошибка сервера"}, status=500)


# =========================
# ПОСЕЩАЕМОСТЬ
# =========================

@login_required
def attendance_dashboard(request):
    """
    Страница посещаемости.
    """

    data = get_attendance_data(request.user)

    return render(request, "journal/attendance.html", {
        "data": data
    })


# =========================
# РУЧНОЕ ДОБАВЛЕНИЕ ОЦЕНКИ
# =========================

@login_required
@role_required([Role.ADMIN, Role.TEACHER])
def add_grade(request):
    """
    Форма ручного добавления оценки.
    """

    form = GradeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        lesson_id = request.POST.get("lesson_id")

        if lesson_id is not None:
            try:
                lesson_id = int(lesson_id)
            except ValueError:
                return redirect("journal")

        set_grade(
            user=request.user,
            cadet_id=form.cleaned_data["cadet"].id,
            lesson_id=lesson_id,
            value=form.cleaned_data["value"],
        )

        return redirect("journal")

    return render(request, "journal/add_grade.html", {"form": form})