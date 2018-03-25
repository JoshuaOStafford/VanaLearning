from django.shortcuts import render, redirect
from Reports.models import Student, DRC, MasterDRC, Teacher, Parent
from datetime import datetime, timezone
import datetime as datetime3
from django.contrib.auth.decorators import login_required
import pytz
from datetime import timedelta, date, datetime as datetime2
from Reports.functions import get_user, log_drc, get_different_week_url, get_teachers_data_setup, calculate_past_week_data,\
    calculate_current_week_data, get_week_string, get_monday, get_raw_week_data_total, past_five_days_log_strings, \
    get_raw_week_data_single


@login_required(login_url="/")
def home(request):
    user = get_user(request)
    if user in Teacher.objects.all():
        return redirect('/log')
    # elif user in Parent.objects.all():
    #     return redirect('/day')
    else:
        return redirect('/')


def day_view(request):
    user = get_user(request)
    if user != Teacher.objects.get(username='max'):
        return redirect('/')
    student = Student.objects.get(user.username)
    if request.method == 'POST':
        current_date = request.POST.get('date', False)
    else:
        tz = pytz.timezone('US/Eastern')
        current_date = datetime.now(tz)
    if MasterDRC.objects.filter(date=current_date, student=student):
        drc = MasterDRC.objects.get(date=current_date, student=student)
    else:
        drc = None
    return render(request, 'day.html', {'user': user, 'drc': drc, 'student': student})

def landing_page_view(request):
    child = None
    user = get_user(request)
    return render(request, 'landing_page.html', {'user': user, 'child': child, 'request': request})


def schedule_demo(request):
    return render(request, "schedule_demo.html", context=None)


@login_required(login_url="/")
def log_drc_view(request):
    form_string = '/log'
    tz = pytz.timezone('US/Eastern')
    date = datetime.now(tz)
    date_raw = datetime.now()
    if date_raw.strftime("%A") != date.strftime("%A"):
        date_raw = date_raw + timedelta(days=-1)
    date_string = date.strftime("%A, %B %d")
    teacher = get_user(request)
    if teacher not in Teacher.objects.all():
        return redirect('/home')
    past_five_days = past_five_days_log_strings(date_raw, teacher)
    students = teacher.student_set.all()
    if teacher.username == 'lhorich':
        students = []
        students.append(Student.objects.get(username='max'))
        students.append(Student.objects.get(username='tuppy'))

    remaining_students = []
    for student in students:
        if not DRC.objects.filter(student=student, teacher=teacher, date=date_raw).exists():
            remaining_students.append(student)

    completed_students = []
    for student in students:
        if DRC.objects.filter(student=student, teacher=teacher, date=date_raw).exists():
            drc = DRC.objects.get(student=student, teacher=teacher, date=date_raw)
            completed_students.append({'name': student.name, 'm1': drc.m1, 'm2': drc.m2, 'm3': drc.m3, 'm4': drc.m5, 'homework': drc.m3 != None, 'absent': drc.absent})

    if request.method == 'POST':
        for student in students:
            log_drc(request, student, teacher, date_raw, True)
        return redirect('/log')
    return render(request, 'log_reports.html', {'user': teacher, 'remaining_students': remaining_students, 'completed_students': completed_students,
                                                'are_remaining_students': len(remaining_students) != 0, 'are_completed_students': len(completed_students) != 0,
                                                'form_string': form_string, 'past_five_days': past_five_days, 'date_string': date_string})


@login_required(login_url="/")
def log_past_drc_view(request, date_str):
    form_string = '/log/' + date_str
    is_past = True
    old_date = datetime2.strptime(date_str, '%Y-%m-%d')
    prev_date_str = old_date.strftime("%A, %B %d")
    tz = pytz.timezone('US/Eastern')
    current_date = datetime.now(tz)
    date_raw = datetime.now()
    if date_raw.strftime("%A") != current_date.strftime("%A"):
        date_raw = date_raw + timedelta(days=-1)
    teacher = get_user(request)
    if teacher is None:
        return redirect('/home')
    past_five_days = past_five_days_log_strings(date_raw, teacher)
    students = teacher.student_set.all()
    if teacher.username == 'lhorich':
        students = []
        students.append(Student.objects.get(username='max'))
        students.append(Student.objects.get(username='tuppy'))

    remaining_students = []
    for student in students:
        if not DRC.objects.filter(student=student, teacher=teacher, date=old_date).exists():
            remaining_students.append(student)

    completed_students = []
    for student in students:
        if DRC.objects.filter(student=student, teacher=teacher, date=old_date).exists():
            drc = DRC.objects.get(student=student, teacher=teacher, date=old_date)
            completed_students.append({'name': student.name, 'm1': drc.m1, 'm2': drc.m2, 'm3': drc.m3, 'm4': drc.m5,
                                       'homework': drc.m3 != None, 'absent': drc.absent})

    if request.method == 'POST':
        for student in students:
            log_drc(request, student, teacher, old_date, True)
        return redirect('/log/' + date_str)
    return render(request, 'log_reports.html', {'user': teacher, 'remaining_students': remaining_students, 'completed_students': completed_students,
                                                'are_remaining_students': len(remaining_students) != 0, 'are_completed_students': len(completed_students) != 0,
                                                'is_past': is_past, 'past_string': prev_date_str, 'form_string': form_string,
                                                'past_five_days': past_five_days, 'date_string': prev_date_str})


@login_required(login_url="/")
def raw_week_view(request, student_username):
    child = None
    user = get_user(request)
    # if user is not None and user.type == 'Parent':
    #     child = user.student
    if not Student.objects.filter(username=student_username).exists():
        return redirect('/home')
    student = Student.objects.get(username=student_username)
    today = date.today()
    starting_date = date(2017, 12, 10)
    this_monday = get_monday(today, 0)
    current_monday = this_monday
    weeks_data_array = []
    while current_monday > starting_date:
        if user == Teacher.objects.get(username='lhorich') or user == Teacher.objects.get(username='mdemers') or user == Teacher.objects.get(username='cmiller'):
            metrics = get_raw_week_data_total(current_monday, student, (current_monday == this_monday))
        else:
            metrics = get_raw_week_data_single(current_monday, student, (current_monday == this_monday), user)
        week = {'week_str': get_week_string(current_monday), 'metric1': metrics['m1'], 'metric2': metrics['m2'], 'metric3': metrics['m3'],
                'metric4': metrics['m4']}
        if current_monday != this_monday:
            if not metrics['empty']:
                weeks_data_array.append(week)
        else:
            weeks_data_array.append(week)
        current_monday -= timedelta(days=7)

    return render(request, 'raw_week_data.html', {'user': user, 'child': child, 'student': student,
                                                          'weeks_data_array': weeks_data_array})



@login_required(login_url="/")
def graph_view(request, student_username, start_date_str, end_date_str):
    child = None
    user = get_user(request)
    # if user.type == 'Parent':
    #     child = user.student

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
                return redirect('/graph/' + student_username + '/' + date1_str + "/to/" + date2_str)

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

            if MasterDRC.objects.filter(student=student, date=current_date).exists():
                master_drc = MasterDRC.objects.get(student=student, date=current_date)
                if not master_drc.absent:
                    xaxis_dates.append(current_date_string)
                    yaxis_m1_values.append(master_drc.get_m1_history_charted(4))
                    yaxis_m2_values.append(master_drc.get_m5_history_charted(4))
                    yaxis_m3_values.append(master_drc.get_m3_charted())
                    yaxis_m4_values.append(master_drc.get_m2_history_charted(4))
            # else:
            #     yaxis_m1_values.append(-1)
            #     yaxis_m2_values.append(-1)
            #     yaxis_m3_values.append(-1)
            #     yaxis_m4_values.append(-1)
        current_date = current_date + timedelta(days=1)

    return render(request, "line_graph.html", {'xaxis_dates': xaxis_dates, 'yaxis_m1_data': yaxis_m1_values,
                                                 'yaxis_m2_data': yaxis_m2_values, 'yaxis_m3_data': yaxis_m3_values,
                                                 'yaxis_m4_data': yaxis_m4_values, 'student': student, 'past_week_link': past_week_link,
                                                 'past_2weeks_link': past_2weeks_link, 'past_month_link': past_month_link,
                                                 'current_link': current_link, 'errorMsg': error_msg, 'student_username': student_username,
                                               'user': user, 'child': child})


@login_required(login_url="/")
def current_week_redirect(request, student_username):
    today = datetime3.date.today()
    today_str = today.strftime('%Y-%m-%d')
    past_week_link = get_different_week_url(today_str, -6)
    return redirect("/graph/" + student_username + '/' + past_week_link)


@login_required(login_url="/")
def insights_view(request, student_username):
    child = None
    user = get_user(request)
    student = Student.objects.get(username=student_username)
    if student == Student.objects.get(username='max'):
        return render(request, 'insights/Max_Insights.html', {'user': user, 'child': child})
    elif student == Student.objects.get(username='tuppy'):
        return render(request, 'insights/Tuppy_Insights.html', {'user': user, 'child': child})
    elif student == Student.objects.get(username='jack'):
        return render(request, 'insights/Jack_Insights.html', {'user': user, 'child': child})
    elif student == Student.objects.get(username='tyler'):
        return render(request, 'insights/Tyler_Insights.html', {'user': user, 'child': child})
    elif student == Student.objects.get(username='jalen'):
        return render(request, 'insights/Jalen_Insights.html', {'user': user, 'child': child})
    else:
        return redirect('/log')




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

