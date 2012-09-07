from django.conf.urls.defaults import patterns, include, url
from .views import *


urlpatterns = UserCRUDL().as_urlpatterns()
