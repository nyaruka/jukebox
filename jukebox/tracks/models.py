from django.db import models
from smartmin.models import SmartModel
from mutagen.mp3 import MP3
import mutagen
from tempfile import mktemp
import os
from django.core.files import File
import time

class Artist(SmartModel):
    name = models.CharField(max_length=64, unique=True,
                            help_text="The name of this artist")

    def __unicode__(self):
        return self.name

class Album(SmartModel):
    name = models.CharField(max_length=64, unique=True,
                         help_text="The name of this album")
    artist = models.ForeignKey(Artist,
                           help_text="The artist who recorded this album")
    year = models.IntegerField(null=True, blank=True,
                               help_text="The year this album was released")
    cover = models.ImageField(upload_to="covers", null=True, blank=True,
                              help_text="The cover art if there is one")

    def update_album_art(self, mp3_file):
        mp3_data = MP3(mp3_file)

        if 'APIC:' in mp3_data:
            tmp_name = mktemp()
            tmp_file = open(tmp_name, 'wb')
            tmp_file.write(mp3_data['APIC:'].data)
            tmp_file.close()

            tmp_file = open(tmp_name, 'r')
            self.cover.save('%s.jpg' % self.name, File(tmp_file), save=True)
            self.save()
            
            os.unlink(tmp_name)
        else:
            tmp_name = mktemp()
            tmp_file = open(tmp_name, 'wb')
            default_cover = open("jukebox.png",'r')
            tmp_file.write(default_cover.read())
            tmp_file.close()

            tmp_file = open(tmp_name, 'r')
            self.cover.save('%s.jpg' % self.name, File(tmp_file), save=True)
            self.save()
            
            os.unlink(tmp_name)
            
                       
            
            

    def __unicode__(self):
        return self.name

class Genre(SmartModel):
    name = models.CharField(max_length=32, unique=True,
                        help_text="The name of this genre")

    def __unicode__(self):
        return self.name

class Track(SmartModel): 
    name = models.CharField(max_length=128, 
                            help_text="The name of this track")
    length = models.IntegerField(null=True,
                                 help_text="The length of this track in seconds")
    genre = models.ForeignKey(Genre, null=True, blank=True,
                              help_text="The genre for this track")
    album = models.ForeignKey(Album, null=True, blank=True, related_name='tracks',
                              help_text="What album this track belongs to")
    mp3_file = models.FileField(upload_to="mp3s",
                                help_text="The mp3 file that contains the music")

    def update_from_file(self, mp3_file):
        """
        Creates a new Track, Album and Artist from the given mp3 file.  You will be returned
        a Track object with the associated items
        """
	audio = mutagen.File(mp3_file, easy=True)
        user = self.created_by

        genres = Genre.objects.filter(name__iexact=audio['genre'][0])
        if not genres:
            genre = Genre.objects.create(name=audio['genre'][0],
                                         created_by=user,
                                         modified_by=user)
        else:
            genre = genres[0]

        artists = Artist.objects.filter(name__iexact=audio['artist'][0])
        if not artists:
            artist = Artist.objects.create(name=audio['artist'][0],
                                           created_by=user,
                                           modified_by=user)
        else:
            artist = artists[0]

        albums = Album.objects.filter(name__iexact=audio['album'][0])
        if not albums:
            album = Album.objects.create(name=audio['album'][0],
                                         artist=artist,
                                         year=audio.get('date', [None])[0],
                                         created_by=user,
                                         modified_by=user)
        else:
            album = albums[0]

        self.name = audio['title'][0]
        self.album = album
        self.genre = genre
        self.length = audio.info.length

        return self

    def get_length(self):
        return time.strftime('%M:%S', time.gmtime(self.length))

    def __unicode__(self):
        return self.name
    

    



