from django.db.models import Count
from smartmin.views import *
from .models import *
from django.core.cache import cache
from django import forms
from tracks.models import *
from django.shortcuts import redirect
import cPickle as pickle
import json

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
        model = Request

class RequestCRUDL(SmartCRUDL):
    model = Request
    actions = ('read', 'list', 'new','playing', 'radio')

    class Playing(SmartListView):
        refresh = 1000
        permission = None
        
        def get_queryset(self):
            return Request.objects.filter(status__in= ["P","Q"]).order_by('created_on')

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

        def get_queryset(self, *args, **kwargs):
            queryset = None
            cacheResult = False
            
            # grab our redis client connection
            redis = cache.client.client

            if not redis.exists('requests'):
                queryset = super(RequestCRUDL.List, self).get_queryset(*args, **kwargs)
                result = []
                for request in list(queryset[:100]):
                    result.append(request.as_dict())
                    redis.rpush('requests', pickle.dumps(request.as_dict(), -1))
            else:
                result = [pickle.loads(_) for _ in redis.lrange('requests', 0, 100)]

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

            cache.client.client.lpush('requests', pickle.dumps(obj_dict, -1))

            # if there is no next up track, set it
            if not cache.client.client.get('next_up'):
                cache.client.client.set('next_up', pickle.dumps(obj_dict, -1))                

            return obj

    class Radio(SmartListView):
        def get_queryset(self, **kwargs):
            return Request.objects.filter(created_by=self.request.user).values('track__album__artist__name', 'track__name', 'track__mp3_file').distinct().order_by('?')[:10]
