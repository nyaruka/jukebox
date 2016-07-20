from django.db import models
from smartmin.models import SmartModel
from jukebox.tracks.models import *
import datetime
import time
import pickle


class Request(SmartModel):
    STATUS_CHOICES = (('Q', "Queued"),
                      ('P', "Playing"),
                      ('C', "Complete"))

    track = models.ForeignKey(Track,
                              help_text="The track that has been requested", related_name="requests")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='Q',
                              help_text="Whether the request is queued, playing or complete")
    played_on = models.DateTimeField(null=True, blank=True)

    def get_progress(self):
        if self.status == "P":
            progress = (self.get_elapsed()*100 /self.track.length)
        else:
            progress = 0
        return progress

    def get_formatted_elapsed(self):
        
        return time.strftime('%M:%S',time.gmtime(self.get_elapsed()))

    def get_elapsed(self):
        if self.status == "P":
            diff = (datetime.datetime.now()- self.played_on).total_seconds()
        else:
            diff = 0
        return diff

    def __unicode__(self):
        return "[%s] %s" % (self.status, self.track.name)

    def as_dict(self):
        album = None
        if self.track.album:
            album = dict(id=self.track.album.id,
                         name=self.track.album.name,
                         cover=self.track.album.cover,
                         artist=dict(id=self.track.album.artist.id,
                                     name=self.track.album.artist.name))

            if self.track.album.cover:
                album['cover'] = self.track.album.cover.path
            else:
                album['cover'] = None

        return dict(id=self.id,
                    played_on=self.played_on,
                    created_on=self.created_on,
                    created_by=dict(id=self.created_by.id,
                                    username=self.created_by.username,
                                    first_name=self.created_by.first_name,
                                    last_name=self.created_by.last_name),
                    track=dict(id=self.track.id,
                               name=self.track.name,
                               album=album,
                               length=self.track.length))

class Vote(SmartModel):
    request = models.ForeignKey(Request,
                                help_text="The request that was voted on")
    track = models.ForeignKey(Track,
                              help_text="The track being voted on", related_name="votes")
    score = models.IntegerField(help_text="The score attributed to this vote")


