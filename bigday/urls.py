from django.conf.urls import url, include
from django.contrib import admin

from django.conf.urls import handler404, handler500

urlpatterns = [
    url(r'^', include('wedding.urls')),
    url(r'^', include('guests.urls')),
    url(r'^admin/', admin.site.urls),
    url('^accounts/', include('django.contrib.auth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

handler404 = 'guests.views.vhandler404'
handler500 = 'guests.views.vhandler500'