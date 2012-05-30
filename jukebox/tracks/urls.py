from .views import *

urlpatterns = ArtistCRUDL().as_urlpatterns()
urlpatterns += TrackCRUDL().as_urlpatterns()
urlpatterns += AlbumCRUDL().as_urlpatterns()
urlpatterns += GenreCRUDL().as_urlpatterns()
