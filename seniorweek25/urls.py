from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', lambda request: HttpResponseRedirect('/seniorweek25/lottery/')),
    url(r'^lottery/', include('lottery.urls')),
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/',  'mit.scripts_login',  name='login', ),
    
)
