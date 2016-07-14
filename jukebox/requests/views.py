from smartmin.views import *
from .models import *
from django.core.cache import cache
from django import forms
from jukebox.tracks.models import *
from django.shortcuts import redirect
from django_redis import get_redis_connection
import cPickle as pickle

class RequestForm(forms.ModelForm):
    tracks = Track.objects.filter(is_active=True).exclude(name='')

    track = forms.ModelChoiceField(tracks)

    def clean(self):
        cleaned_data = super(RequestForm, self).clean()
        cleaned_data['on_list'] = False
        data = cleaned_data['track']
        on_queue = Request.objects.filter(track=data, status__in=['Q', 'P'])
        if on_queue:
            cleaned_data['on_list'] = True
        return cleaned_data

    class Meta:
        fields = ('track',)
        model = Request

class RequestCRUDL(SmartCRUDL):
    model = Request
    actions = ('read', 'list', 'new','playing', 'radio')

    class Playing(SmartTemplateView):
        permission = None
        template = 'requests/request_playing.html'

    class List(SmartListView):
        permission = None
        title = "Playlist"
        paginate_by = 25
        select_related = ('track__name', 'track__album__cover', 'track__album__name', 
                          'track__album__artist__name', 'created_by__first_name', 'created_by__last_name')
        default_order = ('-created_on',)
        fields = ('track', 'status', 'created_by', 'created_on')
        field_config = { 'track': dict(label="Song"),
                         'created_by': dict(label="Requested By") }

        def get_context_data(self, *args, **kwargs):
            context = super(RequestCRUDL.List, self).get_context_data(*args, **kwargs)
            requests = context['object_list']
            if requests:
                context['first'] = requests[0]
            else:
                context['first'] = dict(id=-1)

            return context

        def get_queryset(self, *args, **kwargs):
            r = get_redis_connection("default")

            if not self.request.GET.keys():
                if not r.exists('requests'):
                    queryset = super(RequestCRUDL.List, self).get_queryset(*args, **kwargs)
                    result = []
                    for request in list(queryset[:25]):
                        result.append(request.as_dict())
                        r.rpush('requests', pickle.dumps(request.as_dict(), -1))
                else:
                    result = [pickle.loads(_) for _ in r.lrange('requests', 0, 25)]
            else:
                result = super(RequestCRUDL.List, self).get_queryset(*args, **kwargs)

            return result

        def get_status(self, obj):
            return obj.get_status_display()

    class New(SmartCreateView):
        fields = ('track',)
        success_url = '@requests.request_list'
        form_class = RequestForm

        def form_valid(self, form):
            if form.cleaned_data['on_list'] == True:
                return redirect(reverse('requests.request_list'))
            else:
                return super(RequestCRUDL.New, self).form_valid(form)

        def post_save(self, obj):
            obj = super(RequestCRUDL.New, self).post_save(obj)
            obj_dict = obj.as_dict()

            r = get_redis_connection("default")
            r.lpush('requests', pickle.dumps(obj_dict, -1))

            # if there is no next up track, set it
            if not r.get('next_up'):
                r.set('next_up', pickle.dumps(obj_dict, -1))

            return obj

    class Radio(SmartListView):
        def get_queryset(self, **kwargs):
            return Request.objects.filter(created_by=self.request.user).values('track__album__artist__name', 'track__name', 'track__mp3_file').distinct().order_by('?')[:10]
