from django.db import models
from smartmin.models import SmartModel
from mutagen.mp3 import MP3
import mutagen
from tempfile import mktemp
import os
from django.core.files import File
import time
import re
from urllib2 import urlopen
from urllib import quote_plus
from time import sleep

class Artist(SmartModel):
    name = models.CharField(max_length=64, unique=True,
                            help_text="The name of this artist")

    def cover(self):
        for album in self.albums.all():
            if album.cover:
                return album.cover
        return None

    def __unicode__(self):
        return self.name

class Album(SmartModel):
    name = models.CharField(max_length=64, unique=True,
                         help_text="The name of this album")
    artist = models.ForeignKey(Artist,
                           help_text="The artist who recorded this album", related_name="albums")
    year = models.IntegerField(null=True, blank=True,
                               help_text="The year this album was released")
    cover = models.ImageField(upload_to="covers", null=True, blank=True,
                              help_text="The cover art if there is one")

    @classmethod
    def fix_album_art(cls):
        # get all tracks with no art
        for track in Track.objects.filter(album__cover=""):
            album = Album.objects.get(pk=track.album.pk)
            if not album.cover:
                album.find_album_art(track.name)

    def fetch_image_url(self, query_string):
        got_result = False
        tries = 0
        
        while tries < 3:
            try:
                url = "http://www.albumart.org/index.php?skey=" + quote_plus(query_string) + "&itempage=1&newsearch=1&searchindex=Music"
                print "fetching: %s" % url
                content = urlopen(url).read()
                match = re.search('.*href="(.*?)" title="View larger image"', content)
                if match: 
                    return match.group(1)
                else:
                    return None
            except:
                sleep(10)

    def find_album_art(self, track_name=None):
        album_name = re.sub('([^a-zA-Z0-9])', ' ', self.name)
        album_name = re.sub('( +)', ' ', album_name)

        artist_name = re.sub('([^a-zA-Z0-9])', ' ', self.artist.name)
        artist_name = re.sub('( +)', ' ', artist_name)

        search_string = album_name + " " + artist_name
        image_url = self.fetch_image_url(search_string)

        if not image_url:
            image_url = self.fetch_image_url(album_name)

        if not image_url:
            image_url = self.fetch_image_url(artist_name)

        if not image_url and track_name:
            track_name = re.sub('([^a-zA-Z0-9])', ' ', track_name)
            track_name = re.sub('( +)', ' ', track_name)
            image_url = self.fetch_image_url(track_name)

        # found a match, woo!
        if image_url:
            try:
                image = urlopen(image_url)

                tmp_name = mktemp()
                tmp_file = open(tmp_name, 'wb')
                tmp_file.write(image.read())
                tmp_file.close()

                tmp_file = open(tmp_name, 'r')
                self.cover.save('%s.jpg' % self.name, File(tmp_file), save=True)
                self.save()
            
                os.unlink(tmp_name)
                print "found match: %s" % image_url
                return image_url
            except:
                return None

        else:
            print "No image found"
            return None
            
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


    def up_votes(self):
        return self.votes.filter(score=1)

    def down_votes(self):
        return self.votes.filter(score=-1)

    def user_requests(self):
        return self.requests.exclude(created_by_id=-1)

    def update_from_file(self, mp3_file):
        """
        Creates a new Track, Album and Artist from the given mp3 file.  You will be returned
        a Track object with the associated items
        """

        audio = mutagen.File(mp3_file, easy=True)
        user = self.created_by

        album_name = "Unknown"
        if 'album' in audio:
            album_name = audio['album'][0][:64]

        artist_name = audio['artist'][0][:64]
        track_title = audio['title'][0][:128]

        genre = None
        genre_name = None
        if 'genre' in audio:
            genre_name = audio['genre'][0][:64]


        # take the first genre if its csv
        if genre_name:
            genre_name = genre_name.split(',')[0]


        if genre_name:
            genres = Genre.objects.filter(name__iexact=genre_name)
            if not genres:
                genre = Genre.objects.create(name=genre_name,
                                         created_by=user,
                                         modified_by=user)
            else:
                genre = genres[0]


        artists = Artist.objects.filter(name__iexact=artist_name)
        if not artists:
            artist = Artist.objects.create(name=artist_name,
                                           created_by=user,
                                           modified_by=user)
        else:
            artist = artists[0]

        albums = Album.objects.filter(artist=artist,
                                      name__iexact=album_name)
        if not albums:
            year = audio.get('date', None)
            if year:
                match = re.search('(\d\d\d\d)', year[0])
                if match:
                    year = match.group(1)
                else:
                    year = None

            album = Album.objects.create(name=album_name,
                                         artist=artist,
                                         year=year,
                                         created_by=user,
                                         modified_by=user)
        else:
            album = albums[0]

        self.name = track_title
        self.album = album
        self.genre = genre
        self.length = audio.info.length

        return self

    def get_length(self):
        return time.strftime('%M:%S', time.gmtime(self.length))

    def __unicode__(self):
        return self.name
    
