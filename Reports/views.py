from django.shortcuts import render, redirect
from Reports.models import Student, DRC, MasterDRC, Teacher
from datetime import datetime, timezone
import datetime as datetime3
from django.contrib.auth.decorators import login_required
from Reports.functions import get_user, log_drc, get_different_week_url, get_teachers_data_setup, calculate_past_week_data, calculate_current_week_data, get_week_string, get_monday, get_raw_week_data
import pytz
from datetime import timedelta, date, datetime as datetime2


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
def student_raw_week_view(request, student_username):
    teacher = get_user(request)
    if teacher != Teacher.objects.get(username='lhorich'):
        return redirect('/home')
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    today = date.today()
    starting_date = date(2017, 12, 10)
    this_monday = get_monday(today, 0)
    current_monday = this_monday
    weeks_data_array = []
    while current_monday > starting_date:
        metrics = get_raw_week_data(current_monday, student, (current_monday == this_monday))
        week = {'week_str': get_week_string(current_monday), 'metric1': metrics['m1'], 'metric2': metrics['m2'], 'metric3': metrics['m3'],
                'metric4': metrics['m4']}
        if current_monday != this_monday:
            if not metrics['empty']:
                weeks_data_array.append(week)
        else:
            weeks_data_array.append(week)
        current_monday -= timedelta(days=7)

    return render(request, 'student_raw_week_data.html', {'user': teacher, 'student': student,
                                                          'weeks_data_array': weeks_data_array})



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
                        'success1': 'More attentive than last week', 'success2': '', 'success3': '', 'aoi1': 'Homework completion and organization fell 25% and 23% from last week, respectively. ', 'aoi2': '', 'aoi3': '',
                        'insight1': "Teachers completed an average of 1.6 reports per day (compared with 2 per day last week)",
                        'insight2': "", 'insight3': '', 'attendance': 5}

    elif student.username == 'max':
        week1_report = {'m1yes': 8, 'm2yes': 8, 'm3yes': 5, 'm4yes': 9, 'total': 9, 'hw_total': 6,
                        'm1percent': 89, 'm2percent': 89, 'm3percent': 83, 'm4percent': 100,
                        'success1': 'Second week in a row with an average of at least 90%', 'success2': '', 'success3': '', 'aoi1': 'Received a disproportionate amount of No\'s on Wednesday\'s for the second week in a row (50% of all his "No\'s over the past two weeks occurred on the two wednesdays)', 'aoi2': '', 'aoi3': '',
                        'insight1': "Did not get more than one “No” on any measures", 'insight2': "Teachers completed an average of 2.25 reports per day (compared with 1.5 last week)", 'insight3': '', 'attendance': 4}

    elif student.username == 'tuppy':
        week1_report = {'m1yes': 5, 'm2yes': 5, 'm3yes': 4, 'm4yes': 6, 'total': 8, 'hw_total': 4,
                        'm1percent': 63, 'm2percent': 63, 'm3percent': 100, 'm4percent': 75,
                        'success1': 'Significantly more attentive than last week', 'success2': 'Performed 50% better this Wednesday than last Wednesday', 'success3': '', 'aoi1': 'Second week in a row with a combined average of Appropriate Behavior and Attentive in the low 60%',
                        'aoi2': 'Performed 50% worse this Friday than last Friday', 'aoi3': 'Behavioral consistency. The percentage of time he received a rating of Yes, rather than No, on all tracked behaviors varied significantly each day. From Monday to Friday, respectively, he received the following proportion of yeses: 33%, 100%, 86%, 57%, and 70%. ',
                        'insight1': "Teachers completed an average of 2 reports per day (compared with 1.25 last week)", 'insight2': "Teachers engaged rose steadily throughout the week", 'insight3': '',
                        'attendance': 4}

    elif student.username == 'tyler':
        week1_report = {'m1yes': 4, 'm2yes': 4, 'm3yes': 0, 'm4yes': 4, 'total': 4, 'hw_total': 0,
                        'm1percent': 100, 'm2percent': 100, 'm3percent': 100, 'm4percent': 100,
                        'success1': '100% effectiveness on every documented measure for the second week in a row', 'success2': '', 'success3': '', 'aoi1': '', 'aoi2': '', 'aoi3': '',
                        'insight1': "Was given 0 homework assignments all week. ", 'insight2': "Over the past two weeks, he has been given “Yes” marks 100% of them time on every tracked behavior, from 100% of his teachers. ", 'insight3': "Teachers completed an average of 2 reports per day (compared with 1.4 last week)", 'attendance': 2}

    elif student.username == 'jack':
        week1_report = {'m1yes': 11, 'm2yes': 11, 'm3yes': 6, 'm4yes': 10, 'total': 11, 'hw_total': 6,
                        'm1percent': 100, 'm2percent': 100, 'm3percent': 100, 'm4percent': 91,
                        'success1': '100% homework completion, which was higher than last week\'s percentage even though he had more homeworks', 'success2': '', 'success3': '', 'aoi1': '', 'aoi2': '', 'aoi3': '',
                        'insight1': "Had better attendance than last week", 'insight2': "Teachers completed an average of 2.2 reports per day (compared with 1.33 last week)", 'insight3': '', 'attendance': 5}

    else:
        return redirect('/home')
    if student not in teacher.student_set.all():
        return redirect('/home')
    return render(request, 'weekly_reports.html', {'user': teacher, 'student': student, 'wr1': week1_report})


@login_required(login_url="/")
def track_reports_view(request):
    admin = get_user(request)
    if not admin == Teacher.objects.get(username='lhorich'):
        return redirect('/home')

    tz = pytz.timezone('US/Eastern')
    today = date.today()
    last_monday = get_monday(today, 1)
    this_monday = get_monday(today, 0)
    past_week = get_week_string(last_monday)
    this_week = get_week_string(this_monday)

    teachers = get_teachers_data_setup()
    teachers = calculate_past_week_data(teachers, last_monday)

    teachers = calculate_current_week_data(teachers, this_monday)

    return render(request, 'teacher_submissions.html', {'user': admin, 'teachers': teachers, 'past_week':
                                                        past_week, 'this_week': this_week})

