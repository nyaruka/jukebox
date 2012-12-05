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
        refresh = 30000
        paginate_by = 75
        default_order = ('-created_on',)
        fields = ('track', 'status', 'created_by', 'created_on')
        field_config = { 'track': dict(label="Song"),
                         'created_by': dict(label="Requested By") }

        def get_context_data(self, **kwargs):
            context = super(RequestCRUDL.List, self).get_context_data(**kwargs)

            top_requests = Request.objects.exclude(created_by=settings.ANONYMOUS_USER_ID).values(
                'track', 'track__album__artist', 'track__album', 'track__name', 'track__album__artist__name',
                'track__album__name', 'track__album__cover').annotate(requested=Count('track',)).filter(requested__gt=1).order_by('-requested')[:25]

            context['top_requests'] = top_requests
            return context

        def get_status(self, obj):
            return obj.get_status_display()

    class New(SmartCreateView):
        fields = ('track',)
        success_url = '@requests.request_list'

    class Radio(SmartListView):
        def get_queryset(self, **kwargs):
            return Request.objects.filter(created_by=self.request.user).values('track__album__artist__name', 'track__name', 'track__mp3_file').distinct().order_by('?')[:10]