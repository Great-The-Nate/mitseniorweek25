import os
import math

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from lottery.models import Student, Event, Wager, Attendance

EVENTS =  Event.objects.all()

@login_required
def index(request):

	if request.user.username not in ['nmustafa', 'kyna', 'fdma2405', 'claire25', 'stella24', 'yycliang', 'sallyz21', 'katieac', 'jkim25']:
		return render(request, 'lottery/pre_round_2.html')

	error_message = request.session.pop('error_message', None)
	submit_message = request.session.pop('submit_message', None)
	context = {
		'events_list': EVENTS,
		'error_message': error_message, 
		'submit_message': submit_message
	}

	return render(request, 'lottery/lottery.html', context)	


@login_required
def submit(request):
	if request.user.username not in ['nmustafa', 'kyna', 'fdma2405', 'claire25', 'stella24', 'yycliang', 'sallyz21', 'katieac', 'jkim25']:
		return redirect('lottery_home')

	if request.method != 'POST':
		return HttpResponse("Invalid request.")
	
	kerb = request.user.username
	student, _ = Student.objects.get_or_create(kerb=kerb)

	wagers = []
	total_points = 0
	attendances = []
	timestamp = timezone.now()
	for event in EVENTS:
		value = request.POST.get(event.name)
		if not value:
			continue

		if not event.biddable:
			if value not in ['yes', 'no', 'maybe']:
				request.session['error_message'] = "Invalid value for %s." % event
				return redirect('lottery_home')
			attendances.append(Attendance(student_kerb=student, event_id=event, attendance=value, timestamp=timestamp))
			continue

		points = 0
		try:
			points = math.floor(float(value))
			if points < 0 or points > 1000:
				raise ValueError			
		except ValueError:
			request.session['error_message'] = "Invalid value for %s." % event
			return redirect('lottery_home')
		
		if points == 0:
			continue
		
		total_points += points
		if total_points > 1000:
			request.session['error_message'] = "Please submit at most 1000 points."
			return redirect('lottery_home')

		wagers.append(Wager(student_kerb=student, event_id=event, points=points, timestamp=timestamp))

	Wager.objects.bulk_create(wagers)
	Attendance.objects.bulk_create(attendances)
		
	request.session['submit_message'] = "Successfully submitted."
	return redirect('lottery_home')
