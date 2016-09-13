from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^signup$', signup),
    url(r'^verify/(?P<code>[a-f0-9]+)$', verify),
    url(r'^login$', login),
    url(r'^explorer$', explorer),
    url(r'^detail/(?P<Id>\d+)$', detail),
    url(r'^upload$', upload),
    url(r'^comment$', comment),
]
