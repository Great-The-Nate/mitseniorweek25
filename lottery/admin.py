from django.contrib import admin
from lottery.models import Student, Event, Wager

# Register your models here.
admin.site.register(Student)
admin.site.register(Event)
admin.site.register(Wager)
