from django.db import models
from smartmin.models import SmartModel
from tracks.models import *
import datetime

class Request(SmartModel):
    STATUS_CHOICES = (('Q', "Queued"),
                      ('P', "Playing"),
                      ('C', "Complete"))

    track = models.ForeignKey(Track,
                              help_text="The track that has been requested")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='Q',
                              help_text="Whether the request is queued, playing or complete")
    played_on = models.DateTimeField(auto_now_add= True)

    def get_progress(self):
        if self.status == "P":
            progress = (self.get_elapsed()*100 /self.track.length)
        else:
            progress = 0
        return progress

    def get_elapsed(self):
        if self.status == "P":
            diff = (datetime.datetime.now()- self.played_on).total_seconds()
        else:
            diff = 0
        return diff

    def __unicode__(self):
	return "[%s] %s" % (self.status, self.track.name)
    
