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
    child = None
    user = get_user(request)
    # if user is not None and user.type == 'Parent':
    #     child = user.student
    return render(request, 'day.html', {'user': user, 'child': child})

def landing_page_view(request):
    child = None
    user = get_user(request)
    # if user is not None and user.type == 'Parent':
    #     child = user.student
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
    # if user is not None and user.type == 'Parent':
    #     child = user.student
    # if user is None or not Student.objects.filter(username=student_username).exists():
    #     return redirect('/home')
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

    # if user in Teacher.objects.all():
    #     if student not in user.student_set.all():
    #         return redirect('/home')
    # elif user.type == 'Parent':
    #     if student != user.student:
    #         return redirect('/home')
    return render(request, 'weekly_reports.html', {'user': user, 'child': child, 'student': student, 'wr1': week1_report})


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

