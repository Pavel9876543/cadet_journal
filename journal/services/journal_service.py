"""
Сервис формирования журнала (таблицы оценок).
"""

from collections import defaultdict

from journal.models import (
    Group,
    Subject,
    SubjectGroup,
    Cadet,
    Lesson,
    Grade,
    SubjectResult
)

from journal.utils.roles import get_user_role, Role
from journal.services.grade_service import calculate_average_for_cadet_subject


# =========================
# ОСНОВНОЙ СЕРВИС ЖУРНАЛА
# =========================

def get_journal_data(*, user, group_id=None, subject_id=None):
    """
    Возвращает данные для журнала с учетом роли пользователя.
    """

    role = get_user_role(user)

    groups = Group.objects.all()
    subjects = Subject.objects.all()

    # =========================
    # ДОСТУП ДЛЯ ПРЕПОДАВАТЕЛЯ
    # =========================

    if role == Role.TEACHER:

        teacher = user.teacher

        sg = SubjectGroup.objects.filter(teacher=teacher)

        allowed_groups = list(
            sg.values_list("group_id", flat=True)
        )

        subjects = Subject.objects.filter(
            subject_groups__in=sg
        ).distinct()

    else:
        # админ видит всё
        allowed_groups = list(groups.values_list("id", flat=True))

    # =========================
    # ДЕФОЛТЫ
    # =========================

    if not subject_id and subjects.exists():
        subject_id = str(subjects.first().id)

    if not group_id and allowed_groups:
        group_id = str(allowed_groups[0])

    # защита от подмены
    if group_id and allowed_groups and int(group_id) not in allowed_groups:
        group_id = str(allowed_groups[0])

    # =========================
    # ДАННЫЕ
    # =========================

    cadets = Cadet.objects.filter(
        group_id=group_id
    ).order_by("last_name")

    lessons = Lesson.objects.filter(
        subject_id=subject_id,
        group_id__in=allowed_groups
    ).order_by("date")

    grades = Grade.objects.filter(
        lesson__in=lessons
    ).select_related("lesson", "cadet")

    # =========================
    # СТРУКТУРА ЖУРНАЛА
    # =========================

    journal = defaultdict(dict)

    for grade in grades:
        journal[grade.cadet_id][grade.lesson_id] = grade.value

    # =========================
    # СРЕДНИЕ БАЛЛЫ
    # =========================

    averages = {}

    subject = None
    if subject_id:
        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            subject = None

    for cadet in cadets:
        if subject:
            avg = calculate_average_for_cadet_subject(
                cadet,
                subject
            )
        else:
            avg = None
        averages[cadet.id] = avg

    # =========================
    # ЭКЗАМЕН / ИТОГ
    # =========================

    results = {}

    subject_results = SubjectResult.objects.filter(
        subject_id=subject_id,
        cadet__in=cadets
    )

    for r in subject_results:
        results[r.cadet_id] = {
            "exam": r.exam,
            "final": r.final
        }

    # =========================
    # ДЛЯ JS (фильтрация)
    # =========================

    subject_groups = {}

    for s in Subject.objects.all():
        subject_groups[str(s.id)] = list(
            SubjectGroup.objects.filter(subject=s)
            .values_list("group_id", flat=True)
        )

    return {
        "groups": groups,
        "subjects": subjects,
        "cadets": cadets,
        "lessons": lessons,
        "journal": journal,
        "averages": averages,
        "results": results,
        "subject_id": str(subject_id) if subject_id else "",
        "group_id": str(group_id) if group_id else "",
        "subject_groups": subject_groups,
    }