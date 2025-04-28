from django.conf.urls import patterns, url

from lottery import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='lottery_home'),
    url(r'^submit/', views.submit, name='lottery_submit'),
)
