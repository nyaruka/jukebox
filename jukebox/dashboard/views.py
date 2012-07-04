from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from smartmin.views import *
from django import forms
from django.contrib.auth.decorators import login_required
from rapidsms_httprouter.models import Message
from rapidsms.models import Backend
from django.conf import settings
from requests.models import *
from tracks.models import *
import datetime

@login_required
def index(request):
	requests = Request.objects.all()
	
        progress = None
	for song in requests:
<<<<<<< HEAD
		if song.status == "P":
			progressong = ((datetime.datetime.now() - song.played_on)*100 / song.track.length)
			context = dict(requests = requests, progressong = progressong)
		else:
			context = dict(requests = requests)
=======
                if song.status == "P":
			progress = ((datetime.datetime.now() - song.played_on)*100 / song.track.length)
	context = dict(requests = requests, progress = progress)
>>>>>>> cca92e2969a0e478ad9fa7fdfa2a6d4eaaa7b7c5
	return render_to_response('dashboard/index.html', context, context_instance=RequestContext(request))

def status(request):
    (backend, created) = Backend.objects.get_or_create(name=settings.DEFAULT_BACKEND)
    unsent_count = Message.objects.filter(status__in=['L','Q'], connection__backend=backend).count()
    if unsent_count > 1:
        return HttpResponse("ERROR - UNSENT COUNT: %s" % unsent_count)
    else:
        return HttpResponse("OK")
