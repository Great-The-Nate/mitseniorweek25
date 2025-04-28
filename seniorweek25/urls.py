from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', lambda request: HttpResponseRedirect('/seniorweek25/lottery/'), name='home'),
    url(r'^lottery/', include('lottery.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^cert/login/', 'cert_auth.scripts_login', name='cert_login'),
    url(r'^oidc/', include('oidc_auth.urls'))
)
