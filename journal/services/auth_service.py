"""
Сервис авторизации и проверки доступа.
"""

from django.core.exceptions import PermissionDenied

from journal.models import SubjectGroup, Cadet
from journal.utils.roles import get_user_role, Role


# =========================
# БАЗОВЫЕ ПРОВЕРКИ
# =========================

def require_authenticated(user):
    """
    Проверка, что пользователь авторизован.
    """
    if not user or not user.is_authenticated:
        raise PermissionDenied("Требуется авторизация")


def require_teacher(user):
    """
    Проверка, что пользователь преподаватель.
    """
    if get_user_role(user) != Role.TEACHER:
        raise PermissionDenied("Только для преподавателей")


def require_student(user):
    """
    Проверка, что пользователь студент.
    """
    if get_user_role(user) != Role.STUDENT:
        raise PermissionDenied("Только для студентов")


def require_admin(user):
    """
    Проверка, что пользователь администратор.
    """
    if get_user_role(user) != Role.ADMIN:
        raise PermissionDenied("Только для администратора")


# =========================
# ДОСТУП К ЖУРНАЛУ
# =========================

def check_teacher_access_to_lesson(user, lesson):
    """
    Проверяет, что преподаватель имеет доступ к занятию.
    """

    role = get_user_role(user)

    if role == Role.ADMIN:
        return

    if role != Role.TEACHER:
        raise PermissionDenied("Нет доступа")

    # 🔧 фикс: защита от отсутствия teacher
    if not hasattr(user, "teacher"):
        raise PermissionDenied("Профиль преподавателя не найден")

    teacher = user.teacher

    allowed = SubjectGroup.objects.filter(
        subject=lesson.subject,
        group=lesson.group,
        teacher=teacher
    ).exists()

    if not allowed:
        raise PermissionDenied("Нет доступа к этому занятию")


def check_teacher_access_to_cadet(user, cadet, lesson=None):
    """
    Проверяет, что преподаватель может работать с курсантом.
    """

    role = get_user_role(user)

    if role == Role.ADMIN:
        return

    if role != Role.TEACHER:
        raise PermissionDenied("Нет доступа")

    # 🔧 фикс: защита от отсутствия teacher
    if not hasattr(user, "teacher"):
        raise PermissionDenied("Профиль преподавателя не найден")

    teacher = user.teacher

    # если есть урок — проверяем через него
    if lesson:
        allowed = SubjectGroup.objects.filter(
            subject=lesson.subject,
            group=lesson.group,
            teacher=teacher
        ).exists()

        if not allowed:
            raise PermissionDenied("Нет доступа")

        if cadet.group_id != lesson.group_id:
            raise PermissionDenied("Курсант не из этой группы")

    else:
        # общий доступ — проверяем по группам
        allowed_groups = SubjectGroup.objects.filter(
            teacher=teacher
        ).values_list("group_id", flat=True)

        if cadet.group_id not in allowed_groups:
            raise PermissionDenied("Нет доступа к этому курсанту")


# =========================
# ДОСТУП СТУДЕНТА
# =========================

def check_student_access(user, cadet):
    """
    Студент может видеть только себя.
    """

    role = get_user_role(user)

    if role == Role.ADMIN:
        return

    if role != Role.STUDENT:
        raise PermissionDenied("Нет доступа")

    # 🔧 фикс: защита от отсутствия cadet
    if not hasattr(user, "cadet"):
        raise PermissionDenied("Профиль курсанта не найден")

    if user.cadet.id != cadet.id:
        raise PermissionDenied("Можно смотреть только свои данные")