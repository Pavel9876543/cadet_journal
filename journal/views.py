import json
from collections import defaultdict

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import *

from datetime import datetime

months = {
    'января':1, 'февраля':2, 'марта':3, 'апреля':4,
    'мая':5, 'июня':6, 'июля':7, 'августа':8,
    'сентября':9, 'октября':10, 'ноября':11, 'декабря':12
}

def grade_list(request):
    grades=Grade.objects.all()
    return render(request,"journal/grade_list.html",{"grades":grades})

def journal_table(request):
    """
    Журнал: строки — курсанты, колонки — даты (Lesson)
    """

    group_id = request.GET.get("group")
    subject_id = request.GET.get("subject")

    groups = Group.objects.all()
    subjects = Subject.objects.all()

    # дефолты
    if not subject_id and subjects.exists():
        subject_id = str(subjects.first().id)

    allowed_groups = []

    if subject_id:
        allowed_groups = list(
            SubjectGroup.objects.filter(subject_id=subject_id)
            .values_list("group_id", flat=True)
        )

    if not group_id and allowed_groups:
        group_id = str(allowed_groups[0])

    # курсанты
    cadets = Cadet.objects.filter(group_id=group_id).order_by("last_name")

    # занятия
    lessons = Lesson.objects.filter(
        subject_id=subject_id,
        group_id=group_id
    ).order_by("date")

    # оценки
    grades = Grade.objects.filter(lesson__in=lessons)

    journal = defaultdict(dict)

    for grade in grades:
        journal[grade.cadet_id][grade.lesson_id] = grade.value

    context = {
        "groups": groups,
        "subjects": subjects,
        "cadets": cadets,
        "lessons": lessons,
        "journal": journal,
        "subject_id": subject_id,
        "group_id": group_id,
    }

    return render(request, "journal/journal_table.html", context)

@require_POST
@csrf_exempt
def save_grade(request):
    """
    Сохраняет оценку из ячейки (AJAX)
    """

    if request.method == "POST":

        data = json.loads(request.body)

        cadet_id = data.get("cadet_id")
        lesson_id = data.get("lesson_id")
        value = data.get("value")

        grade, created = Grade.objects.get_or_create(
            cadet_id=cadet_id,
            lesson_id=lesson_id,
        )

        grade.value = value
        grade.save()

        return JsonResponse({"status": "ok"})
