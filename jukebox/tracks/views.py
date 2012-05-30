from smartmin.views import *
from .models import *

class ArtistCRUDL(SmartCRUDL):
    model = Artist
    actions = ('create', 'list', 'read', 'update')

    class List(SmartListView):
        fields = ('name', 'created_on')
        search_fields = ('name__icontains',)

class TrackCRUDL(SmartCRUDL):
    model = Track
    actions = ('create', 'list', 'read', 'update', 'delete')

    class List(SmartListView):
        fields = ('title', 'artist', 'length', 'genre', 'album')
        search_fields = ('title__icontains', 'album__artist__name__icontains')

        def get_artist(self, obj):
            return obj.album.artist.name

        def get_length(self, obj):
            mins = obj.length / 60
            secs = obj.length % 60

            if mins <= 0:
                return "%ds" % secs
            else:
                return "%dm %ds" % (mins, secs)

class AlbumCRUDL(SmartCRUDL):
    model = Album
    actions = ('create', 'list', 'read', 'update')

    class List(SmartListView):
        fields = ('title', 'artist', 'year')


class GenreCRUDL(SmartCRUDL):
    model = Genre
    actions = ('create', 'list', 'read', 'update')

    class List(SmartListView):
        fields = ('name',)




