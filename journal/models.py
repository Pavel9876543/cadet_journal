"""
Модели системы электронного журнала (production-ready).
"""

from django.db import models
from django.contrib.auth.models import User


# =========================
# ГРУППЫ
# =========================

class Group(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


# =========================
# КУРСАНТЫ
# =========================

class Cadet(models.Model):

    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    birth_date = models.DateField()
    phone = models.CharField(max_length=20)

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

    GRADE = "grade"
    PASS_FAIL = "pass_fail"

    TYPE_CHOICES = [
        (GRADE, "Оценка"),
        (PASS_FAIL, "Зачет/Незачет"),
    ]

    name = models.CharField(max_length=200)

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    teachers = models.ManyToManyField(
        Teacher,
        related_name="subjects",
        blank=True
    )

    def __str__(self):
        return self.name


# =========================
# СВЯЗЬ ПРЕДМЕТ ↔ ГРУППА ↔ ПРЕПОДАВАТЕЛЬ
# =========================

class SubjectGroup(models.Model):

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

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    class Meta:
        unique_together = ("subject", "group")

    def __str__(self):
        return f"{self.subject} - {self.group} ({self.teacher})"


# =========================
# ЗАНЯТИЕ
# =========================

class Lesson(models.Model):

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

    value = models.CharField(max_length=10)

    class Meta:
        unique_together = ("cadet", "lesson")

    def __str__(self):
        return f"{self.cadet} - {self.value}"


# =========================
# ИСТОРИЯ ОЦЕНОК (AUDIT)
# =========================

class GradeHistory(models.Model):

    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="history"
    )

    old_value = models.CharField(max_length=10, null=True, blank=True)
    new_value = models.CharField(max_length=10)

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    action = models.CharField(max_length=20, default="updated")

    def __str__(self):
        return f"{self.grade} {self.old_value} → {self.new_value}"


# =========================
# ПОСЕЩАЕМОСТЬ
# =========================

class Attendance(models.Model):

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


# =========================
# ИТОГИ ПО ПРЕДМЕТУ
# =========================

class SubjectResult(models.Model):

    cadet = models.ForeignKey(Cadet, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    exam = models.CharField(max_length=10, default="_", blank=True)
    final = models.CharField(max_length=10, default="_", blank=True)

    class Meta:
        unique_together = ("cadet", "subject")

    def __str__(self):
        return f"{self.cadet} - {self.subject}"