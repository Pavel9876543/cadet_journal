"""
Заполнение БД реалистичными тестовыми данными
под новую архитектуру (Lesson, SubjectGroup).
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from journal.models import (
    Group, Cadet, Teacher,
    Subject, SubjectGroup,
    Lesson, Grade
)


class Command(BaseCommand):

    help = "Заполняет БД реалистичными данными"


    def handle(self, *args, **kwargs):

        self.stdout.write("Очистка БД...")

        Grade.objects.all().delete()
        Lesson.objects.all().delete()
        SubjectGroup.objects.all().delete()
        Subject.objects.all().delete()
        Cadet.objects.all().delete()
        Teacher.objects.all().delete()
        Group.objects.all().delete()


        # =========================
        # ГРУППЫ
        # =========================

        group_names = ["1а", "1б", "2а", "2б", "3а", "3б"]
        groups = [Group.objects.create(name=name) for name in group_names]


        # =========================
        # ПРЕПОДАВАТЕЛИ
        # =========================

        teachers_data = [
            ("Иванов", "Андрей"),
            ("Петров", "Сергей"),
            ("Сидоров", "Олег"),
            ("Кузнецов", "Дмитрий"),
            ("Смирнов", "Алексей"),
        ]

        teachers = []

        for last, first in teachers_data:
            teachers.append(
                Teacher.objects.create(
                    last_name=last,
                    first_name=first
                )
            )


        # =========================
        # ПРЕДМЕТЫ
        # =========================

        subjects_data = [
            ("Тактика", "grade"),
            ("Огневая подготовка", "grade"),
            ("Физическая подготовка", "grade"),
            ("Строевая подготовка", "pass_fail"),
            ("Военная топография", "grade"),
        ]

        subjects = []

        for name, type_ in subjects_data:

            subject = Subject.objects.create(
                name=name,
                type=type_
            )

            subject.teachers.set(random.sample(teachers, 2))

            subjects.append(subject)


        # =========================
        # SUBJECT ↔ GROUP
        # =========================

        for subject in subjects:
            for group in groups:

                # старшие курсы имеют больше предметов
                if group.name.startswith("3") or random.random() > 0.3:

                    SubjectGroup.objects.create(
                        subject=subject,
                        group=group
                    )


        # =========================
        # КУРСАНТЫ
        # =========================

        last_names = [
            "Иванов", "Петров", "Сидоров", "Кузнецов",
            "Смирнов", "Попов", "Васильев", "Соколов",
            "Михайлов", "Новиков"
        ]

        first_names = [
            "Алексей", "Дмитрий", "Иван", "Максим",
            "Никита", "Сергей", "Андрей", "Егор"
        ]

        cadets = []

        for group in groups:

            for i in range(15):  # 15 курсантов в группе

                cadet = Cadet.objects.create(
                    last_name=random.choice(last_names),
                    first_name=random.choice(first_names),
                    middle_name="А.",
                    birth_date="2005-01-01",
                    phone="+79000000000",
                    group=group
                )

                cadets.append(cadet)


        # =========================
        # LESSONS (занятия)
        # =========================

        lessons = []

        start_date = date(2025, 9, 1)

        for subject in subjects:

            subject_groups = SubjectGroup.objects.filter(subject=subject)

            for sg in subject_groups:

                current_date = start_date

                for i in range(10):  # 10 занятий

                    lesson = Lesson.objects.create(
                        subject=subject,
                        group=sg.group,
                        teacher=random.choice(teachers),
                        date=current_date
                    )

                    lessons.append(lesson)

                    current_date += timedelta(days=7)


        # =========================
        # ОЦЕНКИ
        # =========================

        grade_values = ["5+", "5", "5-", "4+", "4", "4-", "3", "2"]
        pass_values = ["зачет", "незачет"]

        for lesson in lessons:

            cadets_in_group = Cadet.objects.filter(group=lesson.group)

            for cadet in cadets_in_group:

                # 10% пропусков (нет оценки)
                if random.random() < 0.1:
                    continue

                if lesson.subject.type == "grade":
                    value = random.choice(grade_values)
                else:
                    value = random.choice(pass_values)

                Grade.objects.create(
                    cadet=cadet,
                    lesson=lesson,
                    value=value
                )


        self.stdout.write(self.style.SUCCESS("БД успешно заполнена 🚀"))