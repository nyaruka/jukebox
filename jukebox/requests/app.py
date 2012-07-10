from rapidsms.apps.base import AppBase
from .models import *
from nsms.text import gettext as _
from nsms.parser import Parser, ParseException
from nsms.utils import get_connection_user
from rapidsms.models import Backend, Connection
from django.utils import translation
from rapidsms_httprouter.router import get_router
from django.template import Template, Context
from django.conf import settings
from django.contrib.auth.models import User
from subprocess import call
import re

class App(AppBase):
    
    def handle (self, message):
        parser = Parser(message.text)
        first_word = parser.next_word()

        user = get_connection_user(message.connection)

        if first_word.lower() == 'yay' or first_word.lower() == 'boo':
            playing = Request.objects.filter(status='P')
            if not playing:
                message.respond("There is no playing track to vote on")
                return True
            
            track = playing[0].track
            if first_word.lower() == 'yay':
                score = 1
            else:
                score = -1

            existing = Vote.objects.filter(request=playing[0],
                                           created_by=user)
            if existing:
                message.respond("You have already voted on this request")
                return True
            
            Vote.objects.create(request=playing[0], track=track, score=score,
                                created_by=user, modified_by=user)

            if score == 1:
                message.respond("Your positive vote has been recorded for %s" % track.name)
                call(["mpg123", '/home/precise/Projects/jukebox/jukebox/yay.mp3'])
            else:
                message.respond("Your negative vote has been recorded for %s" % track.name)
                call(["mpg123", '/home/precise/Projects/jukebox/jukebox/boo.mp3'])

        else:
            matching = Track.objects.filter(album__artist__name__icontains=message.text).order_by('?')

            if matching:
                existing = Request.objects.filter(status__in=['Q', 'P'], 
                                                  track__album__artist=matching[0].album.artist)

                if not existing:
                    Request.objects.create(track=matching[0],
                                           created_by=user,
                                           modified_by=user)
                    message.respond("Queuing the track: %s" % matching[0].name)
                else:
                    message.respond("That artist is already in the queue, please pick something else");
            else:
                message.respond("No matching song found for: %s" % message.text)

        return True
