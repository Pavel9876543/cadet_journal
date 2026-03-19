"""
Сервис аналитики посещаемости.
"""

from collections import defaultdict

from journal.models import Attendance, Lesson, Subject, SubjectGroup, Cadet
from journal.utils.roles import get_user_role, Role


# =========================
# БАЗОВЫЙ РАСЧЁТ
# =========================

def calculate_attendance(cadet, subject=None):
    """
    Рассчитывает процент посещаемости.
    """

    lessons = Lesson.objects.filter(group=cadet.group)

    if subject:
        lessons = lessons.filter(subject=subject)

    total = lessons.count()

    if total == 0:
        return 0

    present = Attendance.objects.filter(
        cadet=cadet,
        lesson__in=lessons,
        status=Attendance.PRESENT
    ).count()

    return round((present / total) * 100, 1)


# =========================
# СТУДЕНТ
# =========================

def get_student_attendance(user):
    """
    Посещаемость студента:
    - по предметам
    - общая
    """

    cadet = user.cadet

    subjects = Subject.objects.filter(
        subject_groups__group=cadet.group
    ).distinct()

    by_subject = {}

    for subject in subjects:
        by_subject[subject.name] = calculate_attendance(cadet, subject)

    total = calculate_attendance(cadet)

    return {
        "by_subject": by_subject,
        "total": total
    }


# =========================
# ПРЕПОДАВАТЕЛЬ
# =========================

def get_teacher_attendance(user):
    """
    Посещаемость для преподавателя:
    - по каждому студенту и предмету
    - общий показатель по студентам
    """

    teacher = user.teacher

    sg = SubjectGroup.objects.filter(teacher=teacher)

    by_subject = {}
    total = {}

    for item in sg:

        cadets = Cadet.objects.filter(group=item.group)

        for cadet in cadets:

            key = f"{cadet} ({item.subject})"

            by_subject[key] = calculate_attendance(cadet, item.subject)

            # общий по студенту
            total[cadet] = calculate_attendance(cadet)

    return {
        "by_subject": by_subject,
        "total": total
    }


# =========================
# АДМИН
# =========================

def get_admin_attendance():
    """
    Полная статистика:
    - по предметам
    - общая
    """

    by_subject = {}
    total = {}

    cadets = Cadet.objects.all()
    subjects = Subject.objects.all()

    for cadet in cadets:

        total[cadet] = calculate_attendance(cadet)

        for subject in subjects:
            key = f"{cadet} ({subject})"
            by_subject[key] = calculate_attendance(cadet, subject)

    return {
        "by_subject": by_subject,
        "total": total
    }


# =========================
# УНИВЕРСАЛЬНЫЙ ВХОД
# =========================

def get_attendance_data(user):
    """
    Универсальный вход для views.
    """

    role = get_user_role(user)

    if role == Role.STUDENT:
        return get_student_attendance(user)

    if role == Role.TEACHER:
        return get_teacher_attendance(user)

    if role == Role.ADMIN:
        return get_admin_attendance()

    return {}