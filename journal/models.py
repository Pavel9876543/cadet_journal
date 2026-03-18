"""
Модели системы учета успеваемости курсантов.
Нормализованная структура (production-ready).
"""

from django.db import models
from django.contrib.auth.models import User


# =========================
# ГРУППЫ
# =========================

class Group(models.Model):
    """
    Учебная группа.
    Пример: 1а, 2б
    """
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


# =========================
# КУРСАНТЫ
# =========================

class Cadet(models.Model):
    """
    Курсант.
    """

    last_name = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    middle_name = models.CharField("Отчество", max_length=100, blank=True)

    birth_date = models.DateField("Дата рождения")
    phone = models.CharField("Телефон", max_length=20)

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cadets"
    )

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# =========================
# ПРЕПОДАВАТЕЛИ
# =========================

class Teacher(models.Model):
    """
    Преподаватель.
    """

    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# =========================
# ПРЕДМЕТЫ
# =========================

class Subject(models.Model):
    """
    Учебный предмет.
    """

    GRADE = "grade"
    PASS_FAIL = "pass_fail"

    TYPE_CHOICES = [
        (GRADE, "Оценка"),
        (PASS_FAIL, "Зачет/Незачет"),
    ]

    name = models.CharField("Название", max_length=200)

    type = models.CharField(
        "Тип оценки",
        max_length=20,
        choices=TYPE_CHOICES
    )

    teachers = models.ManyToManyField(
        Teacher,
        related_name="subjects"
    )

    def __str__(self):
        return self.name


# =========================
# СВЯЗЬ ПРЕДМЕТ ↔ ГРУППА
# =========================

class SubjectGroup(models.Model):
    """
    Связь предмета с группой.
    Определяет, в каких группах есть предмет.
    """

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="subject_groups"
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="group_subjects"
    )

    class Meta:
        unique_together = ("subject", "group")

    def __str__(self):
        return f"{self.subject} - {self.group}"


# =========================
# ЗАНЯТИЕ (дата журнала)
# =========================

class Lesson(models.Model):
    """
    Занятие (конкретная дата).
    """

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True
    )

    date = models.DateField()

    class Meta:
        unique_together = ("subject", "group", "date")

    def __str__(self):
        return f"{self.subject} {self.group} {self.date}"


# =========================
# ОЦЕНКИ
# =========================

class Grade(models.Model):
    """
    Оценка курсанта.
    """

    cadet = models.ForeignKey(
        Cadet,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    value = models.CharField(
        "Оценка",
        max_length=10
    )

    class Meta:
        unique_together = ("cadet", "lesson")

    def __str__(self):
        return f"{self.cadet} - {self.value}"


# =========================
# ПОСЕЩАЕМОСТЬ
# =========================

class Attendance(models.Model):
    """
    Посещаемость.
    """

    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"

    STATUS_CHOICES = [
        (PRESENT, "Присутствовал"),
        (ABSENT, "Отсутствовал"),
        (EXCUSED, "Уважительная причина"),
    ]

    cadet = models.ForeignKey(
        Cadet,
        on_delete=models.CASCADE
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PRESENT
    )

    class Meta:
        unique_together = ("cadet", "lesson")