from django.conf.urls import patterns, url

from oidc_auth import views

urlpatterns = patterns('',
    url(r'^auth/$', views.oidc_auth, name='oidc_auth'),
    url(r'^login/$', views.oidc_login, name='oidc_login'),
)
