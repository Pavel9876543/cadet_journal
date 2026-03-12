"""
MANAGEMENT COMMAND
Создает тестовые данные для системы учета успеваемости.

Команда:
python manage.py seed_data
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from journal.models import *


class Command(BaseCommand):
    """
    Команда создания тестовых данных.
    """

    help = "Создает тестовые данные"

    def handle(self, *args, **kwargs):
        """
        Основная функция команды.
        Создает группы, курсантов, преподавателей, предметы и оценки.
        """

        self.stdout.write("Создание тестовых данных...")

        # -------------------------------
        # ГРУППЫ
        # -------------------------------

        groups = ["1а", "1б", "2а", "2б", "3а", "3б"]

        group_objects = []

        for name in groups:
            group, created = Group.objects.get_or_create(name=name)
            group_objects.append(group)

        self.stdout.write("Группы созданы")

        # -------------------------------
        # ПРЕПОДАВАТЕЛИ
        # -------------------------------

        teachers_data = [
            ("Иванов", "Иван", "Иванович"),
            ("Петров", "Петр", "Петрович"),
            ("Сидоров", "Сидор", "Сидорович"),
        ]

        teachers = []

        for last, first, middle in teachers_data:
            teacher, created = Teacher.objects.get_or_create(
                last_name=last,
                first_name=first,
                middle_name=middle
            )
            teachers.append(teacher)

        self.stdout.write("Преподаватели созданы")

        # -------------------------------
        # ПРЕДМЕТЫ
        # -------------------------------

        subjects_data = [
            ("Тактика", "grade"),
            ("Физическая подготовка", "grade"),
            ("Строевая подготовка", "pass_fail"),
        ]

        subjects = []

        for name, gtype in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=name,
                grade_type=gtype
            )

            subject.teachers.set(teachers)

            subjects.append(subject)

        self.stdout.write("Предметы созданы")

        # -------------------------------
        # КУРСАНТЫ
        # -------------------------------

        cadets = []

        for i in range(30):

            cadet = Cadet.objects.create(
                last_name=f"Курсант{i}",
                first_name="Иван",
                middle_name="Иванович",
                birth_date=date(2000, 1, 1),
                phone="000000000",
                group=random.choice(group_objects)
            )

            cadets.append(cadet)

        self.stdout.write("Курсанты созданы")

        # -------------------------------
        # ОЦЕНКИ
        # -------------------------------

        grades_values = [
            "5+",
            "5",
            "5-",
            "4+",
            "4",
            "4-",
            "3",
            "2"
        ]

        start_date = date.today() - timedelta(days=30)

        for cadet in cadets:

            for subject in subjects:

                for i in range(5):

                    Grade.objects.create(
                        cadet=cadet,
                        subject=subject,
                        teacher=random.choice(teachers),
                        date=start_date + timedelta(days=i * 3),
                        value=random.choice(grades_values)
                    )

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно созданы"))