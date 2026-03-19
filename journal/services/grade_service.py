"""
Сервис работы с оценками.
"""

import re

from django.core.exceptions import ValidationError

from journal.models import Grade, GradeHistory, Lesson, SubjectResult, Cadet, Subject
from journal.services.auth_service import (
    check_teacher_access_to_lesson,
    check_teacher_access_to_cadet,
)
from journal.utils.roles import get_user_role, Role


# =========================
# ДОПУСТИМЫЕ ЗНАЧЕНИЯ
# =========================

VALID_VALUES = {
    "_", "н",
    "2", "3", "4", "5",
    "2-", "3-", "4-", "5+",
    "зачет", "незачет"
}


# =========================
# ВАЛИДАЦИЯ
# =========================

def normalize_value(value: str) -> str:
    """
    Нормализация значения.
    """
    if value is None:
        return "_"

    value = str(value).strip().lower()

    if value == "":
        return "_"

    return value


def validate_value(value: str):
    """
    Проверка допустимого значения оценки.
    """

    if value is None:
        raise ValidationError("Пустое значение оценки")

    if not re.match(r"^[0-9+\-а-яА-Я_]+$", value):
        raise ValidationError("Недопустимые символы")

    if value not in VALID_VALUES:
        raise ValidationError("Недопустимое значение оценки")


# =========================
# СОХРАНЕНИЕ ОЦЕНКИ
# =========================

def set_grade(*, user, cadet_id, lesson_id, value):
    """
    Создание или обновление оценки.
    """

    try:
        lesson = Lesson.objects.select_related("subject", "group").get(id=lesson_id)
    except Lesson.DoesNotExist:
        raise ValidationError("Занятие не найдено")

    try:
        cadet = Cadet.objects.get(id=cadet_id)
    except Cadet.DoesNotExist:
        raise ValidationError("Кадет не найден")

    # 🔐 безопасность
    check_teacher_access_to_lesson(user, lesson)
    check_teacher_access_to_cadet(user, cadet, lesson)

    value = normalize_value(value)
    validate_value(value)

    grade, created = Grade.objects.get_or_create(
        cadet=cadet,
        lesson=lesson
    )

    old_value = grade.value if not created else None

    if old_value != value:
        grade.value = value
        grade.save()

        # 🔥 AUDIT
        GradeHistory.objects.create(
            grade=grade,
            old_value=old_value,
            new_value=value,
            changed_by=user,
            action="created" if created else "updated"
        )

    return grade


# =========================
# СРЕДНИЙ БАЛЛ (ПРЕДМЕТ)
# =========================

def calculate_average_for_cadet_subject(cadet, subject):
    """
    Средний балл по предмету.
    """

    grades = Grade.objects.filter(
        cadet=cadet,
        lesson__subject=subject
    )

    values = []

    for g in grades:
        val = g.value

        if val in ["_", "н", "зачет", "незачет"]:
            continue

        try:
            values.append(int(val[0]))  # 5+, 4-
        except:
            continue

    if not values:
        return None

    return round(sum(values) / len(values), 2)


# =========================
# СРЕДНИЙ БАЛЛ (ОБЩИЙ)
# =========================

def calculate_student_average(cadet):
    """
    Общий средний балл по всем предметам.
    """

    subject_ids = set(
        Grade.objects.filter(cadet=cadet)
        .values_list("lesson__subject", flat=True)
    )

    averages = []

    for subject_id in subject_ids:
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            continue

        avg = calculate_average_for_cadet_subject(cadet, subject)

        if avg is not None:
            averages.append(avg)

    if not averages:
        return None

    return round(sum(averages) / len(averages), 2)


# =========================
# ЭКЗАМЕН / ИТОГ
# =========================

def set_subject_result(*, user, cadet_id, subject_id, exam=None, final=None):
    """
    Установка экзамена и итоговой оценки.
    """

    try:
        cadet = Cadet.objects.get(id=cadet_id)
    except Cadet.DoesNotExist:
        raise ValidationError("Кадет не найден")

    from journal.models import Subject, SubjectGroup

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        raise ValidationError("Предмет не найден")

    role = get_user_role(user)

    if role != Role.ADMIN:
        teacher = user.teacher

        allowed = SubjectGroup.objects.filter(
            subject=subject,
            group=cadet.group,
            teacher=teacher
        ).exists()

        if not allowed:
            raise ValidationError("Нет доступа")

    result, _ = SubjectResult.objects.get_or_create(
        cadet=cadet,
        subject=subject
    )

    if exam is not None:
        exam = normalize_value(exam)
        validate_value(exam)
        result.exam = exam

    if final is not None:
        final = normalize_value(final)
        validate_value(final)
        result.final = final

    result.save()

    return result