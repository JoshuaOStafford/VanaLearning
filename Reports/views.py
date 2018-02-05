from django.shortcuts import render, redirect
from Reports.models import Student, DRC, MasterDRC, Teacher
from datetime import datetime, timezone
import datetime as datetime3
from django.contrib.auth.decorators import login_required
from Reports.functions import get_user, log_drc, get_different_week_url
import pytz
from datetime import timedelta, datetime as datetime2


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
def log_pastdrc_view(request):
    msg = ""
    teacher = get_user(request)
    if teacher is None:
        return redirect('/home')
    students = teacher.student_set.all()
    if teacher.username == 'lhorich':
        students=[]
        students.append(Student.objects.get(username='max'))
        students.append(Student.objects.get(username='tuppy'))

    if request.method == 'POST':
        for student in students:
            if not request.POST.get('date', False):
                msg = "Please enter a date"
                return render(request, 'past_reports.html', {'user': teacher, 'remaining_students': students,
                                                'are_remaining_students': len(students) != 0, 'error_msg': msg})
            else:
                old_date = request.POST['date']
                log_drc(request, student, teacher, old_date, True)

        return redirect('/log/PastReports')
    return render(request, 'past_reports.html', {'user': teacher, 'remaining_students': students,
                                                'are_remaining_students': len(students) != 0, 'error_msg': msg})


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
@login_required(login_url="/")
def progress_graph_view(request, student_username, start_date_str, end_date_str):
    teacher = get_user(request)
    if not (teacher == Teacher.objects.get(username='lhorich') or teacher == Teacher.objects.get(username='christine')):
        return redirect('/home')
    error_msg = ""
    if request.method == 'POST':
        date1_str = request.POST.get('date1', False)
        date2_str = request.POST.get('date2', False)
        if not date1_str or not date2_str or len(date1_str) != 10 or len(date2_str) != 10:
            error_msg = "Please enter valid time span."
        else:
            date1 = datetime2.strptime(date1_str, '%Y-%m-%d')
            date2 = datetime2.strptime(date2_str, '%Y-%m-%d')
            if date1 >= date2:
                error_msg = "Please make sure that the start date is before the end date."
            else:
                return redirect('/ProgressGraph/' + student_username + '/' + date1_str + "/to/" + date2_str)

    student = Student.objects.get(username=student_username)
    xaxis_dates = []
    yaxis_m1_values = []
    yaxis_m2_values = []
    yaxis_m3_values = []
    yaxis_m4_values = []
    today = datetime3.date.today()
    today_str = today.strftime('%Y-%m-%d')
    current_link = student_username + '/' + start_date_str + "/to/" + end_date_str
    past_week_link = student_username + '/' + get_different_week_url(today_str, -6)
    past_2weeks_link = student_username + '/' + get_different_week_url(today_str, -14)
    past_month_link = student_username + '/' + get_different_week_url(today_str, -28)
    start_date = datetime2.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime2.strptime(end_date_str, '%Y-%m-%d')
    current_date = start_date
    while current_date != (end_date + timedelta(days=1)):
        dayOfWeek = current_date.strftime('%A')
        if dayOfWeek != 'Saturday' and dayOfWeek != 'Sunday':
            current_date_string = current_date.strftime('%a, %b %d')
            xaxis_dates.append(current_date_string)

            if MasterDRC.objects.filter(student=student, date=current_date).exists():
                master_drc = MasterDRC.objects.get(student=student, date=current_date)
                yaxis_m1_values.append(master_drc.get_m1_charted())
                yaxis_m2_values.append(master_drc.get_m5_charted())
                yaxis_m3_values.append(master_drc.get_m3_charted())
                yaxis_m4_values.append(master_drc.get_m2_charted())
            else:
                yaxis_m1_values.append(-1)
                yaxis_m2_values.append(-1)
                yaxis_m3_values.append(-1)
                yaxis_m4_values.append(-1)
        current_date = current_date + timedelta(days=1)

    return render(request, "progress_graph.html", {'xaxis_dates': xaxis_dates, 'yaxis_m1_data': yaxis_m1_values,
                                                 'yaxis_m2_data': yaxis_m2_values, 'yaxis_m3_data': yaxis_m3_values,
                                                 'yaxis_m4_data': yaxis_m4_values, 'student': student, 'past_week_link': past_week_link,
                                                 'past_2weeks_link': past_2weeks_link, 'past_month_link': past_month_link,
                                                 'current_link': current_link, 'errorMsg': error_msg, 'student_username': student_username,
                                                   'user': teacher})


@login_required(login_url="/")
def current_week_report_redirect(request, student_username):
    today = datetime3.date.today()
    today_str = today.strftime('%Y-%m-%d')
    past_week_link = get_different_week_url(today_str, -6)
    return redirect("/ProgressGraph/" + student_username + '/' + past_week_link)


@login_required(login_url="/")
def weekly_reports_view(request, student_username):
    teacher = get_user(request)
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    week1_report = {}
    if student.username == 'jalen':
        week1_report = {'m1yes': 6, 'm2yes': 6, 'm3yes': 3, 'm4yes': 7, 'total': 9, 'hw_total': 4,
                        'm1percent': 67, 'm2percent': 67, 'm3percent': 75, 'm4percent': 78,
                        'pro_comment1': 'Test #1', 'pro_comment2': 'Test #2', 'con_comment1': 'Test #3', 'con_comment2': 'Test #4'}

    elif student.username == 'max':
        week1_report = {'m1yes': 8, 'm2yes': 8, 'm3yes': 5, 'm4yes': 9, 'total': 9, 'hw_total': 6,
                        'm1percent': 89, 'm2percent': 89, 'm3percent': 83, 'm4percent': 100,
                        'pro_comment1': '', 'pro_comment2': '', 'con_comment1': '', 'con_comment2': ''}

    elif student.username == 'tuppy':
        week1_report = {'m1yes': 5, 'm2yes': 5, 'm3yes': 4, 'm4yes': 6, 'total': 8, 'hw_total': 4,
                        'm1percent': 63, 'm2percent': 63, 'm3percent': 100, 'm4percent': 75,
                        'pro_comment1': '', 'pro_comment2': '', 'con_comment1': '', 'con_comment2': ''}

    elif student.username == 'tyler':
        week1_report = {'m1yes': 4, 'm2yes': 4, 'm3yes': 0, 'm4yes': 4, 'total': 4, 'hw_total': 0,
                        'm1percent': 100, 'm2percent': 100, 'm3percent': 100, 'm4percent': 100,
                        'pro_comment1': '', 'pro_comment2': '', 'con_comment1': '', 'con_comment2': ''}

    elif student.username == 'jack':
        week1_report = {'m1yes': 11, 'm2yes': 11, 'm3yes': 6, 'm4yes': 10, 'total': 11, 'hw_total': 6,
                        'm1percent': 100, 'm2percent': 100, 'm3percent': 100, 'm4percent': 91,
                        'pro_comment1': '', 'pro_comment2': '', 'con_comment1': '', 'con_comment2': ''}

    else:
        return redirect('/home')
    if student not in teacher.student_set.all():
        return redirect('/home')
    return render(request, 'weekly_reports.html', {'user': teacher, 'student': student, 'wr1': week1_report})


@login_required(login_url="/")
def teacher_submissions_view(request):
    teacher = get_user(request)
    if not teacher == Teacher.objects.get(username='lhorich'):
        return redirect('/home')

    tz = pytz.timezone('US/Eastern')
    date = datetime.now(tz)
    date_string = date.strftime("%A, %B %d")

    if request.method == 'POST':
        if request.POST.get('date', False):
            date = request.POST['date']
            current_date = datetime2.strptime(date, '%Y-%m-%d')
            date_string = current_date.strftime("%A, %B %d")
    a6Done = b6Done = c6Done = d6Done = a7Done = b7Done = c7Done = d7Done = a8Done = b8Done = c8Done = d8Done = False
    a6 = DRC.objects.filter(teacher=Teacher.objects.get(username='dbleiberg'), date=date).count()
    if a6 == 1:
        a6Done = True
    b6 = DRC.objects.filter(teacher=Teacher.objects.get(username='mdemers'), date=date).count()
    if b6 == 1:
        b6Done = True
    c6 = DRC.objects.filter(teacher=Teacher.objects.get(username='cwest'), date=date).count()
    if c6 == 1:
        c6Done = True
    d6 = DRC.objects.filter(teacher=Teacher.objects.get(username='vwhite'), date=date).count()
    if d6 == 1:
        d6Done = True
    a7 = DRC.objects.filter(teacher=Teacher.objects.get(username='ghunter'), date=date).count()
    if a7 == 2:
        a7Done = True
    b7 = DRC.objects.filter(teacher=Teacher.objects.get(username='amarusak'), date=date).count()
    if b7 == 2:
        b7Done = True
    c7 = DRC.objects.filter(teacher=Teacher.objects.get(username='cmiller'), date=date).count()
    if c7 == 2:
        c7Done = True
    d7 = DRC.objects.filter(teacher=Teacher.objects.get(username='czolet'), date=date).count()
    if d7 == 2:
        d7Done = True
    a8 = DRC.objects.filter(teacher=Teacher.objects.get(username='mchellman'), date=date).count()
    if a8 == 2:
        a8Done = True
    b8 = DRC.objects.filter(teacher=Teacher.objects.get(username='chenry'), date=date).count()
    if b8 == 2:
        b8Done = True
    c8 = DRC.objects.filter(teacher=Teacher.objects.get(username='cholman'), date=date).count()
    if c8 == 2:
        c8Done = True
    d8 = DRC.objects.filter(teacher=Teacher.objects.get(username='lhorich'), date=date).count()
    if d8 == 2:
        d8Done = True
    return render(request, 'teacher_submissions.html', {'user': teacher, '6a': a6, '6b': b6, '6c': c6, '6d': d6,
                                                        '7a': a7, '7b': b7, '7c': c7, '7d': d7,'8a': a8, '8b': b8,
                                                        '8c': c8, '8d': d8, '6aDone': a6Done, '6bDone': b6Done, '6cDone': c6Done, '6dDone': d6Done,
                                                        '7aDone': a7Done, '7bDone': b7Done, '7cDone': c7Done, '7dDone': d7Done, '8aDone': a8Done, '8bDone': b8Done,
                                                        '8cDone': c8Done, '8dDone': d8Done, 'date': date_string})


