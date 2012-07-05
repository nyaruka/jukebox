from django.core.management.base import BaseCommand, CommandError
import datetime
from optparse import make_option
from requests.models import Request
from tracks.models import Track
from subprocess import call
import sys
import os
from time import sleep
from django.contrib.auth.models import User

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    
    def handle(self, *args, **options):
        tracklib = Track.objects.all()
        lock_file = '/tmp/player.lock'
        user = User.get_anonymous()
        if os.path.exists(lock_file):
            sys.exit(0)
        else:
            call(["touch", lock_file])

        try:
            while(True):
                try:
                    playlist = Request.objects.filter(status='Q').order_by('created_on')
                
                    for request in playlist:
                        request.status = 'P'
                        request.played_on = datetime.datetime.now()
                        request.save()

                        try:
                            
                            call(["mpg123", request.track.mp3_file.path])
                            
			except:
                            import traceback
                            traceback.print_exc()
                            sys.exit(1)
                        finally:
                            request.status = 'C'
                            request.save()
                    
                    if not playlist:
                        randomlist = tracklib.order_by('?')
                        Request.objects.create(track=randomlist[0],
                                           created_by=user,
                                           modified_by=user,
                                           played_on =datetime.datetime.now())
                        
                        
                       
                               

                except:
                    import traceback
                    traceback.print_exc()
                    sys.exit(1)

        finally:
            call(["rm", lock_file])

            
                    
            
