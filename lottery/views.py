from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from lottery.models import Student, Event, Wager

def index(request):
	events = Event.objects.all()
	context = {'events_list': events}
	return render(request, 'lottery.html', context)	

def submit(request):
	if request.method == 'POST':
		results = {} # maps Event instances -> wager amounts for that event
		events = Event.objects.all()
		for event in events:
			field_name = 'event_%d' % event.id
			value = request.POST.get(field_name)
			if value:
				try:
					number = int(value)
					results[event] = number
				except ValueError:
					pass

		total_wagers = sum(results.values())
		if total_wagers > 1000:
			return HttpResponse("You can't wager more than 1000.")
		
		student, _ = Student.objects.get_or_create(kerb="nmustafa")
		student.points = 1000 - total_wagers
		student.save()

		output = "{<br>"
		for event, points in results.items():
			output += "%s: %d<br>" % (event.name, points)

			if points == 0:
				continue

			# Always just insert and we'll ignore duplicates later
			wager = Wager(student_kerb=student, event_id=event, points=points, timestamp=timezone.now())
			wager.save()
			
		return HttpResponse(output+"}")
	else:
		return HttpResponse("Invalid request.")
