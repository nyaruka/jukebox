from django.conf.urls.defaults import patterns, include, url
from .views import *

#home is the view of the playing action of request 
home = RequestCRUDL().view_for_action('playing').as_view()

urlpatterns = RequestCRUDL().as_urlpatterns()
urlpatterns += patterns('', 
                        url(r'^$', home, name='home'),)
