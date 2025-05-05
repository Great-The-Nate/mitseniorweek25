from django.contrib import admin
from lottery.models import Student, Event, Wager, Attendance
 
admin.site.register(Student)
admin.site.register(Event)
admin.site.register(Wager)
admin.site.register(Attendance)