from jukebox.requests.models import Request

def now_playing(request):
    playlist = Request.objects.filter(status__in=['P','Q']).order_by('-created_on')
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
