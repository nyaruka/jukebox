from django.db import models
from smartmin.models import SmartModel
from tracks.models import *

class Request(SmartModel):
    STATUS_CHOICES = (('Q', "Queued"),
                      ('P', "Playing"),
                      ('C', "Complete"))

    track = models.ForeignKey(Track,
                              help_text="The track that has been requested")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='Q',
                              help_text="Whether the request is queued, playing or complete")

    def __unicode__(self):
        return "[%s] %s" % (self.status, self.track.name)
    
