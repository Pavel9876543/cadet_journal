
from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name

class Cadet(models.Model):
    last_name=models.CharField(max_length=100)
    first_name=models.CharField(max_length=100)
    middle_name=models.CharField(max_length=100)
    birth_date=models.DateField()
    phone=models.CharField(max_length=20)
    group=models.ForeignKey(Group,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Teacher(models.Model):
    last_name=models.CharField(max_length=100)
    first_name=models.CharField(max_length=100)
    middle_name=models.CharField(max_length=100)
    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Subject(models.Model):
    GRADE_TYPE=(
    ("grade","Оценка"),
    ("pass_fail","Зачет/Незачет"),
    )
    name=models.CharField(max_length=200)
    grade_type=models.CharField(max_length=20,choices=GRADE_TYPE)
    teachers=models.ManyToManyField(Teacher)
    def __str__(self):
        return self.name

class Grade(models.Model):
    cadet=models.ForeignKey(Cadet,on_delete=models.CASCADE)
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    date=models.DateField()
    value=models.CharField(max_length=10)
    def __str__(self):
        return f"{self.cadet} {self.value}"
