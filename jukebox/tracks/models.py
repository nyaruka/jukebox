from django.db import models
from smartmin.models import SmartModel
import eyeD3

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
    year = models.IntegerField(help_text="The year this album was released")

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
    album = models.ForeignKey(Album, null=True, blank=True,
                              help_text="What album this track belongs to")
    mp3_file = models.FileField(upload_to="mp3s",
                                help_text="The mp3 file that contains the music")

    @classmethod
    def create_from_file(cls, mp3_file, user):
        """
        Creates a new Track, Album and Artist from the given mp3 file.  You will be returned
        a Track object with the associated items
        """
        tag = eyeD3.Tag()
        tag.link(mp3_file)

        genres = Genre.objects.filter(name__iexact=tag.getGenre().name)
        if not genres:
            genre = Genre.objects.create(name=tag.getGenre().name,
                                         created_by=user,
                                         modified_by=user)
        else:
            genre = genres[0]

        artists = Artist.objects.filter(name__iexact=tag.getArtist())
        if not artists:
            artist = Artist.objects.create(name=tag.getArtist(),
                                           created_by=user,
                                           modified_by=user)
        else:
            artist = artists[0]

        albums = Album.objects.filter(name__iexact=tag.getAlbum())
        if not albums:
            album = Album.objects.create(name=tag.getAlbum(),
                                         artist=artist,
                                         year=tag.getYear(),
                                         created_by=user,
                                         modified_by=user)
        else:
            album = albums[0]

        tracks = Track.objects.filter(name__iexact=tag.getTitle(),
                                      album=album)
        if tracks:
            track = tracks[0]
            track.mp3_file =  mp3_file
            track.save()
        else:
            track = Track.objects.create(name=tag.getTitle(),
                                         album=album,
                                         genre=genre,
                                         created_by=user,
                                         modified_by=user)

        return track

    def __unicode__(self):
        return self.name
    

    



