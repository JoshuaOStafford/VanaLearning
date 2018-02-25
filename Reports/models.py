from django.db import models
from datetime import timedelta, date, datetime as datetime2



class Teacher(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=16)
    email = models.EmailField(max_length=50, default='empty@gmail.com')


class Student(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=16)
    teachers = models.ManyToManyField(Teacher)
    m1_name = models.CharField(max_length=40, default='Appropriate Behavior')
    m2_name = models.CharField(max_length=40, default='Attentive')
    m3_name = models.CharField(max_length=40, default='Homework')
    m4_name = models.CharField(max_length=40, default='Needed redirection and reminders')
    m5_name = models.CharField(max_length=40, default='Organized')


class Parent(models.Model):
    name = models.CharField(max_length=30)
    username = models.CharField(max_length=16)
    email = models.EmailField(max_length=50, default='empty@gmail.com')
    student = models.OneToOneField(Student)


class MasterDRC(models.Model):
    date = models.DateField()
    student = models.ForeignKey(Student)
    absent = models.BooleanField(default=False)
    m1_score = models.IntegerField(default=0)
    m2_score = models.IntegerField(default=0)
    m3_score = models.IntegerField(default=0)
    m4_score = models.IntegerField(default=0)
    m5_score = models.IntegerField(default=0)
    HW_Assigned = models.IntegerField(default=0)

    def get_date(self):
        return self.date.strftime("%A, %B %d")

    def get_m1(self):
        total = self.total_count()
        if total == 0:
            return -1
        percentage = round(float(self.m1_score) / total * 100,2)
        return str(percentage)

    def get_m2(self):
        total = self.total_count()
        if total == 0:
            return -1
        percentage = round(float(self.m2_score) / total * 100,2)
        return str(percentage)

    def get_m3(self):
        if self.HW_Assigned <= 0:
            return -1
        percentage = round(float(self.m3_score) / self.HW_Assigned * 100,2)
        return str(percentage)

    def get_m4(self):
        total = self.total_count()
        if total == 0:
            return -1
        percentage = round(float(self.m4_score) / total * 100,2)
        return str(percentage)

    def get_m5(self):
        total = self.total_count()
        if total == 0:
            return -1
        percentage = round(float(self.m5_score) / total * 100,2)
        return str(percentage)

    def get_m1_charted(self):
        return float(self.get_m1())

    def get_m2_charted(self):
        if float(self.get_m2()) - 0.5 < 0:  # if statement ensures charted value will not be negative (range 0-100)
            return self.get_m2()
        return float(self.get_m2()) - .5

    def get_m3_charted(self):
        if float(self.get_m3()) - 1.0 < 0:
            return self.get_m3()
        return float(self.get_m3()) - 1

    def get_m4_charted(self):
        if float(self.get_m4()) - 1.5 < 0:
            return self.get_m4()
        return float(self.get_m4()) - 1.5

    def get_m5_charted(self):
        if float(self.get_m5()) - 2.0 < 0:
            return self.get_m5()
        return float(self.get_m5()) - 2

    def total_count(self):
        total = 0
        for drc in self.drc_set.all():
            if not drc.absent:
                total += 1
        return total

    def get_m1_history_charted(self, days):
        yeses = 0.0
        start_date = self.date
        lookup_date = start_date
        while days > 0:
            current_master = None
            while current_master is None:
                if lookup_date < start_date + timedelta(days=-10):
                    return self.get_m1_charted()
                if MasterDRC.objects.filter(student=self.student, date=lookup_date).exists():
                    current_master = MasterDRC.objects.get(student=self.student, date=lookup_date)
                    yeses += self.get_m1()
                    days -= 1
                    lookup_date = lookup_date + timedelta(days=-1)
                else:
                    lookup_date = lookup_date + timedelta(days=-1)
        return float(yeses/days)


    def get_m2_history_charted(self):
        if float(self.get_m2()) - 0.5 < 0:  # if statement ensures charted value will not be negative (range 0-100)
            return self.get_m2()
        return float(self.get_m2()) - .5

    def get_m3_history_charted(self):
        if float(self.get_m3()) - 1.0 < 0:
            return self.get_m3()
        return float(self.get_m3()) - 1

    def get_m4_history_charted(self):
        if float(self.get_m4()) - 1.5 < 0:
            return self.get_m4()
        return float(self.get_m4()) - 1.5

    def get_m5_history_charted(self):
        if float(self.get_m5()) - 2.0 < 0:
            return self.get_m5()
        return float(self.get_m5()) - 2


class DRC(models.Model):
    # --- identifiers --- #
    date = models.DateField()
    student = models.ForeignKey(Student)
    teacher = models.ForeignKey(Teacher)
    masterDRC = models.ForeignKey(MasterDRC)
    absent = models.BooleanField(default=False)
    # --- metrics --- #
    m1 = models.BooleanField()
    m2 = models.BooleanField()
    m3 = models.NullBooleanField()
    m4 = models.BooleanField()
    m5 = models.BooleanField()
    comments = models.CharField(max_length=500, default="")

    def __str__(self):
        string = self.student.name + " on " + str(self.date) + ": "
        string += self.student.m1_name + ": "
        if self.m1 is True:
            string += 'True'
        else:
            string += 'False'
        string += ', ' + self.student.m2_name + ": "
        if self.m2 is True:
            string += 'True'
        else:
            string += 'False'
        string += ', ' + self.student.m3_name + ": "
        if self.m3 is True:
            string += 'True'
        elif self.m3 is None:
            string += 'N/A'
        else:
            string += 'False'
        string += ', ' + self.student.m4_name + ": "
        if self.m4 is True:
            string += 'True'
        else:
            string += 'False'
        string += ', ' + self.student.m5_name + ": "
        if self.m5 is True:
            string += 'True'
        else:
            string += 'False'
        return string

    def get_date(self):
        return self.date.strftime("%A, %B %d")


# class weeklyreport(models.Model):
#     student = models.ForeignKey(Student)
#     week = models.PositiveIntegerField()
#     m1_score = models.PositiveIntegerField()
#     m2_score = models.PositiveIntegerField()
#     m3_score = models.PositiveIntegerField()
#     m5_score = models.PositiveIntegerField()
#     m1_total = models.PositiveIntegerField()
#     m2_total = models.PositiveIntegerField()
#     m3_total = models.PositiveIntegerField()
#     m5_total = models.PositiveIntegerField()
#     pro_comment1 = models.TextField(max_length=300)
#     pro_comment2 = models.TextField(max_length=300)
#     pro_comment3 = models.TextField(max_length=300)
#     con_comment1 = models.TextField(max_length=300)
#     con_comment2 = models.TextField(max_length=300)
#     con_comment3 = models.TextField(max_length=300)

