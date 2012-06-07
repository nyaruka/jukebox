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

    class Create(SmartCreateView):
        fields = ('mp3_file',)

        def pre_save(self, obj):
            obj = super(TrackCRUDL.Create, self).pre_save(obj)
            return Track.create_from_file(obj.mp3_file.file.temporary_file_path(), obj.created_by)

    class List(SmartListView):
        fields = ('name', 'artist', 'length', 'genre', 'album')
        search_fields = ('name__icontains', 'album__artist__name__icontains')

        def get_artist(self, obj):
            if obj.album:
                return obj.album.artist.name
            else:
                return ""

        def get_length(self, obj):
            if obj.length:
                mins = obj.length / 60
                secs = obj.length % 60

                if mins <= 0:
                    return "%ds" % secs
                else:
                    return "%dm %ds" % (mins, secs)
            else:
                return ""

class AlbumCRUDL(SmartCRUDL):
    model = Album
    actions = ('create', 'list', 'read', 'update')

    class List(SmartListView):
        fields = ('name', 'artist', 'year')


class GenreCRUDL(SmartCRUDL):
    model = Genre
    actions = ('create', 'list', 'read', 'update')

    class List(SmartListView):
        fields = ('name',)




