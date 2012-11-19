from django.core.management.base import BaseCommand, CommandError
import datetime
from optparse import make_option
from requests.models import Request, Vote
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

                        #generate a random track request while no more request to play   
                        # select t.name, count(*) as 'requests', track_id from requests_request, tracks_track t where t.id = requests_request.track_id and requests_request.created_by_id != -1 group by track_id order by requests;

                        # find all songs that have been requested by real users
                        requests = Request.objects.exclude(created_by_id=-1)

                        # now exclude any song that has ever been voted down
                        requests = requests.exclude(track_id__in=[t.id for t in Vote.objects.filter(score=-1)])

                        # exclude anything that has been played recently
                        repeat_window = datetime.timedelta(hours=1)
                        requests = requests.exclude(created_on__gt=datetime.datetime.now() - repeat_window)

                        randomlist = requests.order_by('?')
                        if randomlist:
                            Request.objects.create(track=randomlist[0].track,
                                           created_by=user,
                                           modified_by=user,
                                           played_on =None)
                        
                                                #for the bug of tracks stucking on the playing status because of an unxpected system halt 
                        request_completed = Request.objects.filter(status='P').order_by('created_on')
                        if request_completed:
                            for req in request_completed:
                                if datetime.datetime.now() - req.played_on > req.track.length:
                                    req.status = 'C'
                                    req.save()
                       
                               

                except:
                    import traceback
                    traceback.print_exc()
                    sys.exit(1)

        finally:
            call(["rm", lock_file])

            
                    
            
