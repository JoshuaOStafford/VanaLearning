from django.shortcuts import render, redirect
from Reports.models import Student, DRC, MasterDRC, Teacher
from datetime import datetime, timezone
from django.contrib.auth.decorators import login_required
from Reports.functions import get_user, log_drc
import pytz


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
    tz = pytz.timezone('US/Eastern')
    date = datetime.now(tz)
    total_students = len(teacher.student_set.all())
    if teacher.username == 'lhorich':
        total_students = 2
    reports_logged = len(DRC.objects.filter(teacher=teacher, date=date))
    reports_remaining = total_students - reports_logged
    return render(request, 'home.html', {'user': teacher, 'reports_remaining': reports_remaining})


@login_required(login_url="/")
def log_drc_view(request):
    tz = pytz.timezone('US/Eastern')
    date = datetime.now(tz)
    teacher = get_user(request)
    if teacher is None:
        return redirect('/home')
    students = teacher.student_set.all()
    if teacher.username == 'lhorich':
        students=[]
        students.append(Student.objects.get(username='max'))
        students.append(Student.objects.get(username='tuppy'))
    remaining_students = []
    for student in students:
        if not DRC.objects.filter(student=student, teacher=teacher, date=date).exists():
            remaining_students.append(student)
    if request.method == 'POST':
        for student in students:
            old_date = None
            if not request.POST.get('date', False):
                log_drc(request, student, teacher, old_date, False)
            else:
                old_date = request.POST['date']
                log_drc(request, student, teacher, old_date, True)

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
        if log_drc(request, student, teacher, None, False):
            message = "Report for " + student.name + " has successfully been changed."
        else:
            message = "We failed to change the report for " + student.name + ". Please make sure you entered all " \
                                                                             "five metrics."
    return render(request, 'edit_report.html', {'user': teacher, 'student': student, 'msg': message})


@login_required(login_url="/")
def past_submissions_view(request, student_username):
    tz = pytz.timezone('US/Eastern')
    date = datetime.now(tz)
    d_truncated = date.date()
    teacher = get_user(request)
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    past_drcs = DRC.objects.filter(teacher=teacher, student=student)
    past_drcs = past_drcs.order_by('date')
    past_drcs = past_drcs.reverse()
    return render(request, 'past_submissions.html', {'user': teacher, 'past_drcs': past_drcs, 'student': student,
                                                     'date': date, 'test_date': d_truncated})


@login_required(login_url="/")
def student_history_view(request, student_username):
    teacher = get_user(request)
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    if student not in teacher.student_set.all():
        return redirect('/home')
    master_drcs = MasterDRC.objects.filter(student=student)
    master_drcs = master_drcs.order_by('date')
    master_drcs = master_drcs.reverse()
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


@login_required(login_url="/")
def teacher_submissions_view(request):
    teacher = get_user(request)
    if not teacher == Teacher.objects.get(username='lhorich'):
        return redirect('/home')

    tz = pytz.timezone('US/Eastern')
    date = datetime.now(tz)
    if request.method == 'POST':
        if request.POST.get('date', False):
            date = request.POST['date']
    a6 = DRC.objects.filter(teacher=Teacher.objects.get(username='dbleiberg'), date=date).count()
    b6 = DRC.objects.filter(teacher=Teacher.objects.get(username='mdemers'), date=date).count()
    c6 = DRC.objects.filter(teacher=Teacher.objects.get(username='cwest'), date=date).count()
    d6 = DRC.objects.filter(teacher=Teacher.objects.get(username='vwhite'), date=date).count()

    a7 = DRC.objects.filter(teacher=Teacher.objects.get(username='ghunter'), date=date).count()
    b7 = DRC.objects.filter(teacher=Teacher.objects.get(username='amarusak'), date=date).count()
    c7 = DRC.objects.filter(teacher=Teacher.objects.get(username='cmiller'), date=date).count()
    d7 = DRC.objects.filter(teacher=Teacher.objects.get(username='czolet'), date=date).count()

    a8 = DRC.objects.filter(teacher=Teacher.objects.get(username='mchellman'), date=date).count()
    b8 = DRC.objects.filter(teacher=Teacher.objects.get(username='chenry'), date=date).count()
    c8 = DRC.objects.filter(teacher=Teacher.objects.get(username='cholman'), date=date).count()
    d8 = DRC.objects.filter(teacher=Teacher.objects.get(username='lhorich'), date=date).count()

    return render(request, 'teacher_submissions.html', {'user': teacher, '6a': a6, '6b': b6, '6c': c6, '6d': d6,
                                                        '7a': a7, '7b': b7, '7c': c7, '7d': d7,'8a': a8, '8b': b8,
                                                        '8c': c8, '8d': d8})


