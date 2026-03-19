"""
Общий комментарий:
Кастомные template filters для безопасной работы со словарями и вложенными структурами.
Позволяет избежать падений шаблона при отсутствии ключей.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Функция:
    Безопасно получает значение из словаря по ключу.

    Параметры:
    dictionary — словарь или dict-подобный объект
    key — ключ

    Возвращает:
    значение по ключу или None, если ключ отсутствует
    """
    try:
        if dictionary is None:
            return None
        return dictionary.get(key)
    except Exception:
        return None