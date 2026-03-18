from django.core.management.base import BaseCommand
from journal.models import (
    Group, Subject, SubjectGroup,
    Teacher, Lesson, Grade, Cadet
)
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Полное заполнение базы (группы, курсанты, занятия, оценки)"

    def handle(self, *args, **kwargs):

        self.stdout.write("🧹 Очистка базы...")

        Grade.objects.all().delete()
        Lesson.objects.all().delete()
        SubjectGroup.objects.all().delete()
        Subject.objects.all().delete()
        Cadet.objects.all().delete()
        Group.objects.all().delete()
        Teacher.objects.all().delete()

        self.stdout.write("✅ База очищена")

        # =========================
        # ГРУППЫ
        # =========================

        groups = {}
        for name in ["1а", "1б", "2а", "2б", "3а", "3б"]:
            groups[name] = Group.objects.create(name=name)

        # =========================
        # ПРЕПОДАВАТЕЛИ
        # =========================

        teachers = [
            Teacher.objects.create(last_name="Иванов", first_name="Иван"),
            Teacher.objects.create(last_name="Петров", first_name="Алексей"),
            Teacher.objects.create(last_name="Сидоров", first_name="Максим"),
        ]

        # =========================
        # ПРЕДМЕТЫ
        # =========================

        subjects = {
            "Тактика": Subject.objects.create(name="Тактика", type="grade"),
            "Огневая подготовка": Subject.objects.create(name="Огневая подготовка", type="grade"),
            "Физическая подготовка": Subject.objects.create(name="Физическая подготовка", type="pass_fail"),
            "Строевая подготовка": Subject.objects.create(name="Строевая подготовка", type="pass_fail"),
            "Военная топография": Subject.objects.create(name="Военная топография", type="grade"),
            "Связь": Subject.objects.create(name="Связь", type="grade"),
        }

        # назначаем преподавателей
        for subject in subjects.values():
            subject.teachers.add(random.choice(teachers))

        # =========================
        # СВЯЗИ ПРЕДМЕТ ↔ ГРУППА
        # =========================

        # общие
        for group in groups.values():
            for subject in [
                subjects["Тактика"],
                subjects["Огневая подготовка"],
                subjects["Физическая подготовка"],
            ]:
                SubjectGroup.objects.create(subject=subject, group=group)

        # частично
        for g in ["1а", "1б", "2а", "2б"]:
            SubjectGroup.objects.create(
                subject=subjects["Строевая подготовка"],
                group=groups[g]
            )

        # индивидуальные
        for g in ["2а", "2б"]:
            SubjectGroup.objects.create(
                subject=subjects["Военная топография"],
                group=groups[g]
            )

        for g in ["3а", "3б"]:
            SubjectGroup.objects.create(
                subject=subjects["Связь"],
                group=groups[g]
            )

        # =========================
        # КУРСАНТЫ
        # =========================

        last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Попов"]
        first_names = ["Иван", "Алексей", "Максим", "Дмитрий", "Егор", "Никита"]

        cadets = []

        for group in groups.values():
            for _ in range(15):  # по 15 человек
                cadet = Cadet.objects.create(
                    last_name=random.choice(last_names),
                    first_name=random.choice(first_names),
                    middle_name="",
                    birth_date=date(2005, random.randint(1, 12), random.randint(1, 28)),
                    phone="+79000000000",
                    group=group
                )
                cadets.append(cadet)

        # =========================
        # ЗАНЯТИЯ
        # =========================

        start_date = date(2025, 9, 1)

        lessons = []

        for sg in SubjectGroup.objects.all():
            for i in range(12):  # 12 занятий
                lesson = Lesson.objects.create(
                    subject=sg.subject,
                    group=sg.group,
                    teacher=random.choice(teachers),
                    date=start_date + timedelta(days=i * 7)
                )
                lessons.append(lesson)

        # =========================
        # ОЦЕНКИ
        # =========================

        grade_values = ["2", "3", "4", "5", "2-", "3-", "4-", "5+"]
        pass_values = ["зачет", "незачет"]

        for lesson in lessons:

            group_cadets = Cadet.objects.filter(group=lesson.group)

            for cadet in group_cadets:

                # шанс пропуска
                if random.random() < 0.15:
                    value = "_"
                else:
                    if lesson.subject.type == "grade":
                        value = random.choice(grade_values)
                    else:
                        value = random.choice(pass_values)

                Grade.objects.create(
                    cadet=cadet,
                    lesson=lesson,
                    value=value
                )

        self.stdout.write(self.style.SUCCESS("🔥 База полностью заполнена"))