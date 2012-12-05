from jukebox.requests.models import Request

def now_playing(request):
    playlist = Request.objects.filter(status__in=['P','Q']).order_by('-created_on')
    if playlist:
        now_playing = None
        next_up = None
        for req in playlist:
            if req.status == 'P':
                now_playing = req
            elif req.status == 'Q':
                next_up = req
            else:
                break
        return dict(now_playing=now_playing, next_up=next_up, playlist=playlist)