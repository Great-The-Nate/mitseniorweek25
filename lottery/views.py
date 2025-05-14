import os
import math
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from lottery.models import Student, Event, Wager, Attendance

EVENTS =  Event.objects.all().order_by('id')

def get_round_one_info(kerb):
	round_one_wagers = Wager.objects.filter(student_kerb=kerb, accepted=True, round=1)
	accepted_event_ids = set()
	for row in round_one_wagers:
		accepted_event_ids.add(row.event_id.id)

	remaining_points = Student.objects.get(kerb=kerb).remaining_points
	return accepted_event_ids, remaining_points

@login_required
def index(request):

	if request.user.username not in ['', 'kyna', 'fdma2405', 'claire25', 'stella24', 'yycliang', 'sallyz21', 'katieac', 'jkim25']:
		return render(request, 'lottery/pre_round_2.html')

	error_message = request.session.pop('error_message', None)
	submit_message = request.session.pop('submit_message', None)

	accepted_event_ids, remaining_points = get_round_one_info(request.user.username)

	round_wagers = Wager.objects.filter(student_kerb=request.user.username, round=2).order_by('-timestamp')
	placed_bid = round_wagers.count() > 0
	latest_wager = {}
	if placed_bid:
		latest_timestamp = round_wagers[0].timestamp
		
		for wager in round_wagers:
			if wager.timestamp == latest_timestamp:
				latest_wager[wager.event_id.id] = wager.points

	event_info = []
	for event in EVENTS:
		event_data = {
			'id': event.id,
			'name': event.name,
			'capacity': event.round_two_capacity,
			'price': event.price,
			'location': event.location,
			'date': event.date,
			'time': event.time,
			'biddable': event.biddable,
			'extra_info': event.extra_info,
			'accepted': event.id in accepted_event_ids,
			# -1 encodes no bid placed yet while 0 means a bit was placed but nothing wagered on this event
			'wagered_points': latest_wager[event.id] if event.id in latest_wager else 0 if placed_bid else -1,
		}
		event_info.append(event_data)
	
	context = {
		'events_list': event_info,
		'error_message': error_message, 
		'submit_message': submit_message,
		'remaining_points': json.dumps(remaining_points),
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
	accepted_event_ids, remaining_points = get_round_one_info(request.user.username)

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

		if event.id in accepted_event_ids:
			request.session['error_message'] = "You have already placed a bid for %s." % event
			return redirect('lottery_home')

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
		if total_points > remaining_points:
			request.session['error_message'] = "Please submit at most %d points." % remaining_points
			return redirect('lottery_home')

		wagers.append(Wager(student_kerb=student, event_id=event, points=points, timestamp=timestamp, accepted=False, round=2))

	Wager.objects.bulk_create(wagers)
	Attendance.objects.bulk_create(attendances)
		
	request.session['submit_message'] = "Successfully submitted. Click on the events below to see your bids."
	return redirect('lottery_home')
