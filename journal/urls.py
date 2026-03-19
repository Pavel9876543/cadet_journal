"""
URL маршруты приложения journal.
"""

from django.urls import path

from journal import views


urlpatterns = [

    # =========================
    # АВТОРИЗАЦИЯ
    # =========================

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),


    # =========================
    # DASHBOARD
    # =========================

    path("", views.dashboard, name="dashboard"),


    # =========================
    # СТУДЕНТ
    # =========================

    path("student/", views.student_dashboard, name="student_dashboard"),


    # =========================
    # ЖУРНАЛ
    # =========================

    path("journal/", views.journal_table, name="journal"),


    # =========================
    # AJAX
    # =========================

    path("save-grade/", views.save_grade, name="save_grade"),
    path("set-result/", views.set_result, name="set_result"),


    # =========================
    # ПОСЕЩАЕМОСТЬ
    # =========================

    path("attendance/", views.attendance_dashboard, name="attendance"),


    # =========================
    # ФОРМЫ
    # =========================

    path("add-grade/", views.add_grade, name="add_grade"),

    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
]