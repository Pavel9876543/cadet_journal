"""
Декораторы для проверки прав доступа (RBAC).
"""

from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from journal.utils.roles import get_user_role, Role


def role_required(allowed_roles):
    """
    Декоратор: доступ только для указанных ролей.

    Пример:
    @role_required([Role.ADMIN, Role.TEACHER])
    """

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            role = get_user_role(request.user)

            if role not in allowed_roles:
                raise PermissionDenied("У вас нет доступа к этой странице")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def teacher_required(view_func):
    """
    Только преподаватель
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        role = get_user_role(request.user)

        if role != Role.TEACHER:
            raise PermissionDenied("Только для преподавателей")

        return view_func(request, *args, **kwargs)

    return wrapper


def student_required(view_func):
    """
    Только студент
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        role = get_user_role(request.user)

        if role != Role.STUDENT:
            raise PermissionDenied("Только для студентов")

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    """
    Только администратор
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        role = get_user_role(request.user)

        if role != Role.ADMIN:
            raise PermissionDenied("Только для администратора")

        return view_func(request, *args, **kwargs)

    return wrapper