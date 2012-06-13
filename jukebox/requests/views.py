from smartmin.views import *
from .models import *

class RequestCRUDL(SmartCRUDL):
    model = Request
    actions = ('create', 'read', 'list', 'new')

    class List(SmartListView):
        default_order = ('-created_on',)
        fields = ('track', 'status', 'created_by', 'created_on')
        field_config = { 'track': dict(label="Song"),
                         'created_by': dict(label="Requested By") }

        def get_status(self, obj):
            return obj.get_status_display()

    class New(SmartCreateView):
        fields = ('track',)
        success_url = '@requests.request_list'

