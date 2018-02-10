from Reports.models import Teacher, DRC, MasterDRC
from django.shortcuts import redirect
import datetime
from datetime import timedelta, datetime as datetime2, date


def get_user(request):
    user = request.user
    if Teacher.objects.filter(username=user.get_username()).exists():
        return Teacher.objects.get(username=user.get_username())
    else:
        return None


def log_drc(request, student, teacher, old_date, is_past_report):
    absent = request.POST.get(student.username + '_absent', False)
    if absent:
        create_absent_drc(student, teacher, old_date, is_past_report)
        return True
    if request.POST.get(student.username + '_m1', False) and request.POST.get(student.username + '_m2', False) \
            and request.POST.get(student.username + '_m3', False) and request.POST.get(student.username + '_m5', False):
        m1 = request.POST[student.username + '_m1']
        m2 = request.POST[student.username + '_m2']
        m3 = request.POST[student.username + '_m3']
        m5 = request.POST[student.username + '_m5']
        comments = request.POST.get(student.username + '_comments', False)
        create_drc(student, teacher, m1, m2, m3, m5, comments, old_date, is_past_report)
        return True
    return False


def create_absent_drc(student, teacher, old_date, is_past_report):
    if is_past_report:
        date = old_date
    else:
        date = datetime.date.today()
    if not MasterDRC.objects.filter(student=student, date=date).exists():
        master_drc = MasterDRC(student=student, date=date, absent=True)
        master_drc.save()
    else:
        master_drc = MasterDRC.objects.get(student=student, date=date)
    if DRC.objects.filter(student=student, date=date, teacher=teacher).exists():
        old_drc = DRC.objects.get(student=student, date=date, teacher=teacher)
        remove_drc_from_master(old_drc, master_drc)
        old_drc.delete()
    drc = DRC(student=student, date=date, teacher=teacher, masterDRC=master_drc, absent=True)
    drc.m1 = False
    drc.m2 = False
    drc.m3 = None
    drc.m4 = False
    drc.m5 = False
    drc.comments = student.username + " was absent today."
    drc.save()
    update_master_drc(drc, master_drc)
    return drc


def create_drc(student, teacher, m1, m2, m3, m5, comments, old_date, is_past_report):
    if is_past_report:
        date = old_date
    else:
        date = datetime.date.today()
    if not MasterDRC.objects.filter(student=student, date=date).exists():
        master_drc = MasterDRC(student=student, date=date, absent=False)
        master_drc.save()
    else:
        master_drc = MasterDRC.objects.get(student=student, date=date)
        master_drc.absent = False
        master_drc.save()
    if DRC.objects.filter(student=student, date=date, teacher=teacher).exists():
        old_drc = DRC.objects.get(student=student, date=date, teacher=teacher)
        remove_drc_from_master(old_drc, master_drc)
        old_drc.delete()
    drc = DRC(student=student, date=date, teacher=teacher, masterDRC=master_drc)

    # set all metrics based on rudimentary logging method that True = 1, False =0, and N/A = 2
    drc.m1 = (m1 == '1')
    drc.m2 = (m2 == '1')
    if m3 == '2':
        drc.m3 = None
    else:
        drc.m3 = (m3 == '1')
    drc.m4 = False
    drc.m5 = (m5 == '1')
    if not comments:
        drc.comments = ''
    else:
        drc.comments = comments
    drc.save()
    update_master_drc(drc, master_drc)
    return drc


def remove_drc_from_master(drc, master_drc):
    if drc.m1:
        master_drc.m1_score -= 1
    if drc.m2:
        master_drc.m2_score -= 1
    if drc.m3:
        master_drc.m3_score -= 1
    if drc.m4:
        master_drc.m4_score -= 1
    if drc.m5:
        master_drc.m5_score -= 1
    if drc.m3 is True or drc.m3 is False:
        master_drc.HW_Assigned -= 1
    master_drc.save()


def update_master_drc(drc, master_drc):
    if drc.m1:
        master_drc.m1_score += 1
    if drc.m2:
        master_drc.m2_score += 1
    if drc.m3:
        master_drc.m3_score += 1
    if drc.m4:
        master_drc.m4_score += 1
    if drc.m5:
        master_drc.m5_score += 1
    if drc.m3 is True or drc.m3 is False:
        master_drc.HW_Assigned += 1
    master_drc.save()


def get_different_week_url(current_date, days_left):
    monday_date = datetime2.strptime(current_date, '%Y-%m-%d')
    start_date = monday_date + timedelta(days=days_left)
    start_date_str = start_date.strftime("%Y-%m-%d")
    link = start_date_str + "/to/" + current_date
    return link


def get_teachers_data_setup():
    teacher1 = {'teacher': Teacher.objects.get(username='dbleiberg'), 'last_week_count': 4, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher2 = {'teacher': Teacher.objects.get(username='mdemers'), 'last_week_count': 4, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher3 = {'teacher': Teacher.objects.get(username='cwest'), 'last_week_count': 4, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher4 = {'teacher': Teacher.objects.get(username='vwhite'), 'last_week_count': 4, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher5 = {'teacher': Teacher.objects.get(username='ghunter'), 'last_week_count': 8, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher6 = {'teacher': Teacher.objects.get(username='amarusak'), 'last_week_count': 8, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher7 = {'teacher': Teacher.objects.get(username='cmiller'), 'last_week_count': 8, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher8 = {'teacher': Teacher.objects.get(username='czolet'), 'last_week_count': 8, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher9 = {'teacher': Teacher.objects.get(username='mchellman'), 'last_week_count': 8, 'last_week_percentage': 0,
                'current_week_count': 0}
    teacher10 = {'teacher': Teacher.objects.get(username='chenry'), 'last_week_count': 8, 'last_week_percentage': 0,
                 'current_week_count': 0}
    teacher11 = {'teacher': Teacher.objects.get(username='cholman'), 'last_week_count': 8, 'last_week_percentage': 0,
                 'current_week_count': 0}
    teacher12 = {'teacher': Teacher.objects.get(username='lhorich'), 'last_week_count': 8, 'last_week_percentage': 0,
                 'current_week_count': 0}
    teachers = [teacher1, teacher2, teacher3, teacher4, teacher5, teacher6,
                teacher7, teacher8, teacher9, teacher10, teacher11, teacher12]
    return teachers


def calculate_past_week_data(teachers, monday):
    for teacher in teachers:
        teacher_object = teacher['teacher']
        total_submissions = 0
        for days_past_monday in range(0, 4):
            current_date = monday + timedelta(days=days_past_monday)
            submissions = 0
            if DRC.objects.filter(date=current_date, teacher=teacher_object).exists():
                submissions = DRC.objects.filter(date=current_date, teacher=teacher_object).count()
            total_submissions += submissions
        teacher['last_week_percentage'] = round(100*(total_submissions/teacher['last_week_count']), 2)
    return teachers


def calculate_current_week_data(teachers, monday):
    for teacher in teachers:
        teacher_object = teacher['teacher']
        total_submissions = 0
        for days_past_monday in range(0, 4):
            current_date = monday + timedelta(days=days_past_monday)
            submissions = 0
            if DRC.objects.filter(date=current_date, teacher=teacher_object).exists():
                submissions = DRC.objects.filter(date=current_date, teacher=teacher_object).count()
            total_submissions += submissions
        teacher['current_week_count'] = total_submissions
    return teachers


def get_week_string(monday):
    return None


def get_monday(today, weeks_ago):
    today = today + timedelta(days=-7*weeks_ago)
    while today.weekday() != 0:
        today = today + timedelta(days=-1)
    return today
