from jukebox.requests.models import Request
import cPickle as pickle
from django_redis import get_redis_connection

def now_playing(request):
    r = get_redis_connection('default')
    now_playing = r.get('now_playing')
    if now_playing: now_playing = pickle.loads(now_playing)

    next_up = r.get('next_up')
    if next_up: next_up = pickle.loads(next_up)

    if not now_playing:
        playlist = Request.objects.filter(status__in=['P','Q']).order_by('-created_on').select_related('track__name', 'track__album__artist__name', 'track__album__cover', 'track__album__name', 'created_by__first_name', 'created_by__last_name')

        if playlist:
            playing = None
            next_up = None

            for req in playlist:
                if req.status == 'P':
                    now_playing = req.as_dict()
                    r.set('now_playing', pickle.dumps(now_playing, -1))
                elif req.status == 'Q':
                    next_up = req.as_dict()
                    r.set('next_up', pickle.dumps(next_up, -1))
                else:
                    break

    return dict(now_playing=now_playing, next_up=next_up)
