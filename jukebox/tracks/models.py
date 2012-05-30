from django.db import models
from smartmin.models import SmartModel

class Artist(SmartModel):
    name = models.CharField(max_length=64, unique=True,
                        help_text="The name of this artist")

    def __unicode__(self):
        return self.name

class Album(SmartModel):
    title = models.CharField(max_length=64, unique=True,
                         help_text="The title of this album")
    artist = models.ForeignKey(Artist,
                           help_text="The artist who recorded this album")
    year = models.IntegerField(help_text="The year this album was released")

    def __unicode__(self):
        return self.title

class Genre(SmartModel):
    name = models.CharField(max_length=32, unique=True,
                        help_text="The name of this genre")

    def __unicode__(self):
        return self.name

class Track(SmartModel):
    title = models.CharField(max_length=128, 
                         help_text="The title of this track")
    length = models.IntegerField(help_text="The length of this track in seconds")
    genre = models.ForeignKey(Genre, null=True, blank=True,
                          help_text="The genre for this track")
    album = models.ForeignKey(Album, null=True, blank=True,
                          help_text="What album this track belongs to")

    def __unicode__(self):
        return self.title
    

    



