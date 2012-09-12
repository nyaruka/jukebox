from smartmin.views import *
from .models import *

class ArtistCRUDL(SmartCRUDL):
    model = Artist
    actions = ('list', 'read', 'update')

    class List(SmartListView):
        fields = ('name', 'created_on')
        search_fields = ('name__icontains',)


class TrackCRUDL(SmartCRUDL):
    model = Track
    actions = ('create', 'list', 'read', 'update', 'delete','playing')

    class Playing(SmartListView):
        refresh = 1000


    class Create(SmartCreateView):
        fields = ('mp3_file',)

        def pre_save(self, obj):
            obj = super(TrackCRUDL.Create, self).pre_save(obj)
            obj.mp3_file.save(obj.mp3_file.name, obj.mp3_file.file, save=True)
            obj.update_from_file(str(obj.mp3_file.file))
            return obj

        def post_save(self, obj):
            obj = super(TrackCRUDL.Create, self).post_save(obj)
            obj.album.update_album_art(str(obj.mp3_file.file))
            return obj

    class List(SmartListView):
        fields = ('name', 'artist', 'length', 'genre', 'album', 'request')
        search_fields = ('name__icontains', 'album__artist__name__icontains')
        default_order = ('-created_on',)

        def derive_queryset(self, **kwargs):
            queryset = super(TrackCRUDL.List, self).derive_queryset(**kwargs)
            return queryset.filter(is_active=True).exclude(name="")

        def get_request(self, obj):
            return '<a class="btn posterize" href="%s?track=%d">Request</a>' % (reverse('requests.request_new'), obj.id)

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
    actions = ('list', 'read', 'update')

    class List(SmartListView):
        fields = ('name', 'artist', 'year')


class GenreCRUDL(SmartCRUDL):
    model = Genre
    actions = ('list', 'read', 'update')

    class List(SmartListView):
        fields = ('name',)




