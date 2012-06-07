from django.test import TestCase
from .models import *
from django.contrib.auth.models import User

class TrackTest(TestCase):

    def test_importing(self):
        user = User.objects.create_user('admin', 'admin@admin.com', 'admin')

        track = Track.create_from_file("../womanizer.mp3", user)

        self.assertEquals(track.name, "Womanizer")
        self.assertEquals(track.album.name, "Circus")
        self.assertEquals(track.album.artist.name, "Britney Spears")
        self.assertEquals(track.genre.name, "Pop")
        
        
