from django.db import models


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
        percentage = round(float(self.m1_score) / total * 100,2)
        return str(percentage)

    def get_m2(self):
        total = self.total_count()
        percentage = round(float(self.m2_score) / total * 100,2)
        return str(percentage)

    def get_m3(self):
        if self.HW_Assigned <= 0:
            return None
        percentage = round(float(self.m3_score) / self.HW_Assigned * 100,2)
        return str(percentage)

    def get_m4(self):
        total = self.total_count()
        percentage = round(float(self.m4_score) / total * 100,2)
        return str(percentage)

    def get_m5(self):
        total = self.total_count()
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
        for drc in self.drc_set:
            if not drc.absent:
                total += 1
        return total


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
