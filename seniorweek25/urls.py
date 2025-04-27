from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'seniorweek25.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', lambda request: HttpResponseRedirect('/seniorweek25/lottery/')),
    url(r'^lottery/', include('lottery.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
