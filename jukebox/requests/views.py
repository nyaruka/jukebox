from django.db.models import Count
from smartmin.views import *
from .models import *

class RequestCRUDL(SmartCRUDL):
    model = Request
    actions = ('read', 'list', 'new','playing', 'radio')

    class Playing(SmartListView):
        refresh = 1000
        permission = None
        
        def get_queryset(self):
            return Request.objects.filter(status__in= ["P","Q"]).order_by('created_on')

    class List(SmartListView):
        title = "Playlist"
        paginate_by = 25
        select_related = ('track__name', 'track__album__cover', 'track__album__name', 
                          'track__album__artist__name', 'created_by__first_name', 'created_by__last_name')
        default_order = ('-created_on',)
        fields = ('track', 'status', 'created_by', 'created_on')
        field_config = { 'track': dict(label="Song"),
                         'created_by': dict(label="Requested By") }

        def get_status(self, obj):
            return obj.get_status_display()

    class New(SmartCreateView):
        fields = ('track',)
        success_url = '@requests.request_list'

    class Radio(SmartListView):
        def get_queryset(self, **kwargs):
            return Request.objects.filter(created_by=self.request.user).values('track__album__artist__name', 'track__name', 'track__mp3_file').distinct().order_by('?')[:10]
