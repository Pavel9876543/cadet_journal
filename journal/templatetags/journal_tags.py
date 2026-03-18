from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Получает значение из словаря.
    """
    if dictionary:
        return dictionary.get(key)