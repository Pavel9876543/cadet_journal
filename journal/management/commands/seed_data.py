"""
Dev seed: реалистичные данные для разработки.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from journal.models import (
    Group, Subject, SubjectGroup,
    Teacher, Lesson, Grade, Cadet,
    Attendance, SubjectResult
)

from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Заполнение тестовыми данными"

    def handle(self, *args, **kwargs):

        self.stdout.write("🧹 Очистка базы...")

        Grade.objects.all().delete()
        Attendance.objects.all().delete()
        Lesson.objects.all().delete()
        SubjectGroup.objects.all().delete()
        Subject.objects.all().delete()
        Cadet.objects.all().delete()
        Group.objects.all().delete()
        Teacher.objects.all().delete()
        SubjectResult.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # =========================
        # ГРУППЫ
        # =========================

        groups = [
            Group.objects.create(name="1а"),
            Group.objects.create(name="2а"),
        ]

        # =========================
        # USERS
        # =========================

        teacher_users = [
            User.objects.create_user(username=f"teacher{i}", password="1234")
            for i in range(1, 4)
        ]

        student_users = [
            User.objects.create_user(username=f"student{i}", password="1234")
            for i in range(1, 6)
        ]

        # =========================
        # ПРЕПОДАВАТЕЛИ
        # =========================

        teachers = []

        for i, user in enumerate(teacher_users):
            teachers.append(
                Teacher.objects.create(
                    last_name=f"Преподаватель{i+1}",
                    first_name="Иван",
                    user=user
                )
            )

        # =========================
        # ПРЕДМЕТЫ
        # =========================

        subjects = [
            Subject.objects.create(name="Тактика", type="grade"),
            Subject.objects.create(name="Огневая", type="grade"),
            Subject.objects.create(name="Физо", type="pass_fail"),
            Subject.objects.create(name="Строевая", type="pass_fail"),
            Subject.objects.create(name="Топография", type="grade"),
        ]

        # =========================
        # SUBJECT ↔ GROUP ↔ TEACHER
        # =========================

        subject_groups = []

        for i, subject in enumerate(subjects):
            for group in groups:

                teacher = teachers[(i + groups.index(group)) % len(teachers)]

                sg = SubjectGroup.objects.create(
                    subject=subject,
                    group=group,
                    teacher=teacher
                )

                subject_groups.append(sg)
                subject.teachers.add(teacher)

        # =========================
        # КУРСАНТЫ (10)
        # =========================

        names = [
            "Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов",
            "Попов", "Соколов", "Лебедев", "Козлов", "Новиков"
        ]

        cadets = []

        for i in range(10):
            cadet = Cadet.objects.create(
                last_name=names[i],
                first_name="Иван",
                birth_date="2005-01-01",
                phone="123",
                group=groups[i % 2],
                user=student_users[i] if i < len(student_users) else None
            )
            cadets.append(cadet)

        # =========================
        # ЗАНЯТИЯ
        # =========================

        base_date = date(2025, 9, 1)
        lessons = []

        for sg in subject_groups:

            used_days = set()  # 🔧 фикс

            for _ in range(3):

                # 🔧 гарантируем уникальный день
                while True:
                    day_offset = random.randint(0, 60)
                    if day_offset not in used_days:
                        used_days.add(day_offset)
                        break

                lesson = Lesson.objects.create(
                    subject=sg.subject,
                    group=sg.group,
                    teacher=sg.teacher,
                    date=base_date + timedelta(days=day_offset)
                )

        # =========================
        # ОЦЕНКИ
        # =========================

        grade_values = ["2", "3", "4", "5", "2-", "4-", "5+", "н", "_"]
        pass_values = ["зачет", "незачет", "н"]

        for lesson in lessons:

            group_cadets = [c for c in cadets if c.group == lesson.group]

            for cadet in group_cadets:

                if lesson.subject.type == "grade":
                    value = random.choice(grade_values)
                else:
                    value = random.choice(pass_values)

                Grade.objects.create(
                    cadet=cadet,
                    lesson=lesson,
                    value=value
                )

                # посещаемость
                Attendance.objects.create(
                    cadet=cadet,
                    lesson=lesson,
                    status=random.choice([
                        Attendance.PRESENT,
                        Attendance.ABSENT,
                        Attendance.EXCUSED
                    ])
                )

        # =========================
        # ЭКЗАМЕН / ИТОГ
        # =========================

        for cadet in cadets:
            for subject in subjects:

                if random.random() < 0.7:

                    SubjectResult.objects.create(
                        cadet=cadet,
                        subject=subject
                        # 🔧 экзамен и итог НЕ заполняем
                    )

        self.stdout.write(self.style.SUCCESS("✅ Данные успешно загружены"))