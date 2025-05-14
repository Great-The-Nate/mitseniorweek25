from django.db import models 

class Student(models.Model):
    kerb = models.CharField(max_length=20, primary_key=True)
    remaining_points = models.IntegerField(default=1000)

    class Meta:
        db_table = 'students'

    def __unicode__(self):
        return self.kerb


class Event(models.Model):
    name = models.CharField(max_length=64)
    date = models.CharField(max_length=128)
    time = models.CharField(max_length=128, null=True)
    location = models.CharField(max_length=128, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    capacity = models.IntegerField(null=True)
    biddable = models.BooleanField(default=True)
    extra_info = models.CharField(max_length=1024, null=True)

    class Meta:
        db_table = 'events'

    def __unicode__(self):
        return self.name
 
 
class Wager(models.Model):
    student_kerb = models.ForeignKey(Student, db_column='student_kerb')
    event_id = models.ForeignKey(Event, db_column='event_id')
    points = models.IntegerField(default=0)
    timestamp = models.DateTimeField()
    round = models.IntegerField(default=1)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = 'lottery_wagers'

    def __unicode__(self):
        return u"(%s, %s, %d)" % (self.student_kerb, self.event_id, self.points)
    
class Attendance(models.Model):
    student_kerb = models.ForeignKey(Student, db_column='student_kerb')
    event_id = models.ForeignKey(Event, db_column='event_id')
    attendance = models.CharField(max_length=8)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'lottery_attendance'

    def __unicode__(self):
        return u"(%s, %s, %s)" % (self.student_kerb, self.event_id, self.attendance)
