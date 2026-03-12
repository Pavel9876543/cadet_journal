
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import *

from datetime import datetime

months = {
    'января':1, 'февраля':2, 'марта':3, 'апреля':4,
    'мая':5, 'июня':6, 'июля':7, 'августа':8,
    'сентября':9, 'октября':10, 'ноября':11, 'декабря':12
}

def grade_list(request):
    grades=Grade.objects.all()
    return render(request,"journal/grade_list.html",{"grades":grades})

def journal_table(request):

    group_id=request.GET.get("group")
    subject_id=request.GET.get("subject")

    cadets=[]
    dates=[]
    journal={}

    # если не выбрано — берем первые
    if not group_id:
        group = Group.objects.first()
        if group:
            group_id = group.id

    if not subject_id:
        subject = Subject.objects.first()
        if subject:
            subject_id = subject.id

    if group_id and subject_id:
        cadets=Cadet.objects.filter(group_id=group_id)
        grades=Grade.objects.filter(cadet__group_id=group_id,subject_id=subject_id)
        dates=sorted(list(set(grades.values_list("date",flat=True))))

        for cadet in cadets:
            journal[cadet]={}
            for date in dates:
                grade=grades.filter(cadet=cadet,date=date).first()
                journal[cadet][date]=grade.value if grade else ""

    context={
    "groups":Group.objects.all(),
    "subjects":Subject.objects.all(),
    "cadets":cadets,
    "dates":dates,
    "journal":journal,
    "subject_id":subject_id
    }

    return render(request,"journal/journal_table.html",context)

@require_POST
def save_journal(request):
    subject_id=request.POST.get("subject_id")

    for key,value in request.POST.items():

        if key.startswith("grade_") and value:

            parts=key.split("_")

            cadet_id=parts[1]
            s = parts[2].replace(" г.", "")
            day, month, year = s.split()
            date = datetime(int(year), months[month], int(day))

            Grade.objects.update_or_create(
            cadet_id=cadet_id,
            subject_id=subject_id,
            date=date,
            defaults={"teacher_id":1,"value":value}
            )

    return redirect(request.META.get("HTTP_REFERER","/"))
