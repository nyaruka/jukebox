from django.core.management.base import BaseCommand, CommandError
import datetime
from jukebox.requests.models import Request, Vote
from subprocess import call
import sys
from django.contrib.auth.models import User
from django_redis import get_redis_connection
import redis
import cPickle as pickle

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    
    def handle(self, *args, **options):
        user = User.get_anonymous()
        r = get_redis_connection('default')

        while(True):
            try:
                playlist = Request.objects.filter(status='Q').order_by('created_on')
                
                for index, request in enumerate(playlist):
                    request.status = 'P'
                    request.played_on = datetime.datetime.now()
                    request.save()

                    try:                            
                        r.set('now_playing', pickle.dumps(request.as_dict(), -1))
                        if index+1 < len(playlist):
                            r.set('next_up', pickle.dumps(playlist[index+1].as_dict(), -1))
                        else:
                            r.delete('next_up')

                        call(["mpg123", request.track.mp3_file.path])
                    except:
                        import traceback
                        traceback.print_exc()
                        sys.exit(1)
                    finally:
                        request.status = 'C'
                        request.save()
                    
                if not playlist:
                    # find all songs that have been requested by real users
                    requests = Request.objects.exclude(created_by_id=-1)

                    # now exclude any song that has ever been voted down
                    requests = requests.exclude(track_id__in=[t.track_id for t in Vote.objects.filter(score=-1)])

                    # exclude anything that has been played recently
                    window = datetime.datetime.now() - datetime.timedelta(hours=6)
                    requests = requests.exclude(track_id__in=[t.track_id for t in Request.objects.filter(created_on__gt=window)])

                    if requests:
                        requests = requests.order_by('?')
                        request = Request.objects.create(track=requests[0].track,
                                                         created_by=user,
                                                         modified_by=user,
                                                         played_on=None)
                        r.lpush('requests', pickle.dumps(request.as_dict(), -1))
                        r.ltrim('requests', 0, 100)
                        
                    # for the bug of tracks stucking on the playing status because of an unxpected system halt 
                    request_completed = Request.objects.filter(status='P').order_by('created_on')
                    for req in request_completed:
                        if long((datetime.datetime.now() - req.played_on).total_seconds()) > req.track.length:
                            req.status = 'C'
                            req.save()

            except:
                import traceback
                traceback.print_exc()
                sys.exit(1)
