from jukebox.requests.models import Request

def now_playing(request):
    playlist = Request.objects.filter(status__in=['P','Q']).order_by('-created_on').select_related('track__name', 'track__album__artist__name', 'track__album__cover', 'track__album__name', 'created_by__first_name', 'created_by__last_name')
    if playlist:
        playing = None
        next_up = None
        for req in playlist:
            if req.status == 'P':
                playing = req
            elif req.status == 'Q':
                next_up = req
            else:
                break

        return dict(now_playing=playing, next_up=next_up, playlist=playlist)
    else:
        return dict()
