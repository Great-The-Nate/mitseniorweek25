import os
import math

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from lottery.models import Event, Wager

EVENTS =  Event.objects.all()

@login_required(login_url='/seniorweek25/accounts/login/')
def index(request):
	# TODO: get previous state based on user for placeholder values? Probably not worth extra load time...
	# TODO: show list of current class of 2025 members / check user is in class of 2025?

	if request.user.username not in ['nmustafa', 'kyna', 'fdma2405', 'claire25', 'stella24', 'yycliang', 'sallyz21', 'katieac', 'jkim25']:
		return HttpResponse("Not yet ;)")

	error_message = request.session.pop('error_message', None)
	submit_message = request.session.pop('submit_message', None)
	context = {
		'events_list': EVENTS,
		'error_message': error_message, 
		'submit_message': submit_message
	}

	return render(request, 'lottery/index.html', context)	


@login_required(login_url='/seniorweek25/accounts/login/')
def submit(request):
	if request.method != 'POST':
		return HttpResponse("Invalid request.")
	
	kerb = request.user.username

	wagers = []
	total_points = 0
	timestamp = timezone.now()
	for event in EVENTS:
		value = request.POST.get(event.name)
		if not value:
			continue

		points = 0
		try:
			points = math.floor(float(value))
			if points < 0 or points > 1000:
				raise ValueError			
		except ValueError:
			request.session['error_message'] = "Invalid value for %s." % event
			return redirect('index')
		
		if points == 0:
			continue
		
		total_points += points
		if total_points > 1000:
			request.session['error_message'] = "Please submit at most 1000 points."
			return redirect('index')

		wagers.append(Wager(student_kerb=kerb, event_id=event, points=points, timestamp=timestamp))

	Wager.objects.bulk_create(wagers)
		
	request.session['submit_message'] = "Successfully submitted."
	return redirect('index')
