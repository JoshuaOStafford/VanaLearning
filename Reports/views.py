from django.shortcuts import render, redirect
from Reports.models import Student, DRC, MasterDRC
import datetime
from django.contrib.auth.decorators import login_required
from Reports.functions import get_user, log_drc


def landing_page_view(request):
    user = get_user(request)
    return render(request, 'landing_page.html', {'user': user})


def schedule_demo(request):
    return render(request, "schedule_demo.html", context=None)


@login_required(login_url="/")
def user_home(request):
    teacher = get_user(request)
    if teacher is None:
        return redirect('/login')
    date = datetime.date.today()
    total_students = len(teacher.student_set.all())
    reports_logged = len(DRC.objects.filter(teacher=teacher, date=date))
    reports_remaining = total_students - reports_logged
    return render(request, 'home.html', {'user': teacher, 'reports_remaining': reports_remaining})


@login_required(login_url="/")
def log_drc_view(request):
    date = datetime.date.today()
    teacher = get_user(request)
    if teacher is None:
        return redirect('/home')
    students = teacher.student_set.all()
    remaining_students = []
    for student in students:
        if not DRC.objects.filter(student=student, teacher=teacher, date=date).exists():
            remaining_students.append(student)
    if request.method == 'POST':
        for student in students:
            log_drc(request, student, teacher)
        return redirect('/log/DailyReports')
    return render(request, 'log_reports.html', {'user': teacher, 'remaining_students': remaining_students,
                                                'are_remaining_students': len(remaining_students) != 0})


@login_required(login_url="/")
def edit_drc_view(request, student_username):
    message = ""
    teacher = get_user(request)
    if teacher is None:
        return redirect('/home')
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    if student not in teacher.student_set.all():
        return redirect('/home')
    if request.method == 'POST':
        if log_drc(request, student, teacher):
            message = "Report for " + student.name + " has successfully been changed."
        else:
            message = "We failed to change the report for " + student.name + ". Please make sure you entered all " \
                                                                             "five metrics."
    return render(request, 'edit_report.html', {'user': teacher, 'student': student, 'msg': message})


@login_required(login_url="/")
def past_submissions_view(request, student_username):
    date = datetime.date.today()
    teacher = get_user(request)
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    past_drcs = DRC.objects.filter(teacher=teacher, student=student)
    return render(request, 'past_submissions.html', {'user': teacher, 'past_drcs': past_drcs, 'student': student,
                                                     'date': date})


@login_required(login_url="/")
def student_history_view(request, student_username):
    teacher = get_user(request)
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    if student not in teacher.student_set.all():
        return redirect('/home')
    master_drcs = MasterDRC.objects.filter(student=student)
    return render(request, 'student_history.html', {'user': teacher, 'student': student, 'Master_DRCs': master_drcs})


@login_required(login_url="/")
def progress_graph_view(request, student_username):
    teacher = get_user(request)
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    if student not in teacher.student_set.all():
        return redirect('/home')
    master_drcs = MasterDRC.objects.filter(student=student)
    return render(request, 'progress_graph.html', {'user': teacher, 'student': student, 'Master_DRCs': master_drcs})


@login_required(login_url="/")
def weekly_reports_view(request, student_username):
    teacher = get_user(request)
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    if student not in teacher.student_set.all():
        return redirect('/home')
    return render(request, 'weekly_reports.html', {'user': teacher, 'student': student})
