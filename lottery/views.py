import os

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required


with open('lottery/data/events.txt', 'r') as f:
    EVENTS = [line.strip() for line in f.readlines() if line.strip()]


@login_required(login_url='/seniorweek25/accounts/login/')
def index(request):
	# TODO: get previous state based on user for placeholder values

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
	if request.method == 'POST':
		kerb = request.user.username
		wagers = []
		total_points = 0
		for event in EVENTS:
			value = request.POST.get(event)
			if not value:
				continue

			points = 0
			try:
				points = int(value)					
			except ValueError:
				request.session['error_message'] = "Invalid value for %s." % event
				return redirect('index')
			
			total_points += points

			if total_points > 1000:
				request.session['error_message'] = "Please submit at most 1000 points."
				return redirect('index')

			wagers.append((event, points))
		
		output = ""
		timestamp = timezone.now().isoformat()
		with open('lottery/data/wagers.txt', 'a') as f:
			for wager in wagers:
				line = "%s\t%s\t%s\t%s\n" % (timestamp, kerb, wager[0], wager[1])
				f.write(line)
				output += line
			
		request.session['submit_message'] = "Successfully submitted."
		return redirect('index')
	else:
		return HttpResponse("Invalid request.")
