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

    # приведение типов
    if group_id:
        group_id = int(group_id)

    if subject_id:
        subject_id = int(subject_id)

    # дефолт предмет
    if not subject_id and subjects.exists():
        subject_id = subjects.first().id

    # доступные группы
    allowed_groups = []

    if subject_id:
        allowed_groups = list(
            SubjectGroup.objects.filter(subject_id=subject_id)
            .values_list("group_id", flat=True)
        )

    # дефолт группа
    if not group_id and allowed_groups:
        group_id = allowed_groups[0]

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

    # 🔥 для JS (обязательно!)
    subject_groups = {}

    for sg in SubjectGroup.objects.all():
        subject_groups.setdefault(str(sg.subject_id), []).append(sg.group_id)

    context = {
        "groups": groups,
        "subjects": subjects,
        "cadets": cadets,
        "lessons": lessons,
        "journal": journal,
        "subject_id": subject_id,
        "group_id": group_id,
        "subject_groups": subject_groups,
    }

    return render(request, "journal/journal_table.html", context)

@require_POST
def save_grade(request):
    """
    Сохраняет оценку (строку!)
    """

    try:
        data = json.loads(request.body)

        cadet_id = data.get("cadet_id")
        lesson_id = data.get("lesson_id")
        value = data.get("value")

        if value:
            value = value.strip()
        else:
            value = "_"

        # защита
        if not cadet_id or not lesson_id:
            return JsonResponse({"error": "Invalid data"}, status=400)

        # обработка значения
        if value is None or value.strip() == "":
            value = None
        else:
            value = value.strip()  # строка, НЕ int

        # сохранение
        Grade.objects.update_or_create(
            cadet_id=cadet_id,
            lesson_id=lesson_id,
            defaults={"value": value}
        )

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)