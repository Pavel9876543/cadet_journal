"""
Определение ролей пользователя и утилиты для работы с ними.
"""

from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    UNKNOWN = "unknown"


def get_user_role(user):
    """
    Определяет роль пользователя.
    """

    if not user or not user.is_authenticated:
        return Role.UNKNOWN

    if user.is_superuser:
        return Role.ADMIN

    # важно: проверяем через hasattr (OneToOneField)
    if hasattr(user, "teacher"):
        return Role.TEACHER

    if hasattr(user, "cadet"):
        return Role.STUDENT

    return Role.UNKNOWN


# =========================
# УДОБНЫЕ ПРОВЕРКИ
# =========================

def is_admin(user):
    return get_user_role(user) == Role.ADMIN


def is_teacher(user):
    return get_user_role(user) == Role.TEACHER


def is_student(user):
    return get_user_role(user) == Role.STUDENT