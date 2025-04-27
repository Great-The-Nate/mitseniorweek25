from django.db import models 
 
class Event(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'events'

    def __unicode__(self):
        return self.name
 
 
class Wager(models.Model):
    student_kerb = models.CharField(max_length=9)
    event_id = models.ForeignKey(Event, db_column='event_id')
    points = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'lottery_wagers'

    def __unicode__(self):
        return u"(%s, %s, %d)" % (self.student_kerb, self.event_id, self.points)