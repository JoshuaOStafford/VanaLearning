from Reports.models import Teacher, DRC, MasterDRC
from django.shortcuts import redirect
import datetime


def get_user(request):
    user = request.user
    if Teacher.objects.filter(username=user.get_username()).exists():
        return Teacher.objects.get(username=user.get_username())
    else:
        return None


def log_drc(request, student, teacher):
    absent = request.POST.get(student.username + '_absent', False)
    if absent:
        create_absent_drc(student, teacher)
        return True
    if request.POST.get(student.username + '_m1', False) and request.POST.get(student.username + '_m2', False) \
            and request.POST.get(student.username + '_m3', False) and request.POST.get(student.username + '_m5', False):
        m1 = request.POST[student.username + '_m1']
        m2 = request.POST[student.username + '_m2']
        m3 = request.POST[student.username + '_m3']
        m5 = request.POST[student.username + '_m5']
        comments = request.POST.get(student.username + '_comments', False)
        create_drc(student, teacher, m1, m2, m3, m5, comments)
        return True
    return False


def create_absent_drc(student, teacher):
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


def create_drc(student, teacher, m1, m2, m3, m5, comments):
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
