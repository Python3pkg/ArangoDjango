# The views used below are normally mapped in django.contrib.admin.urls.py
# This URLs file is used to provide a reliable view deployment for test purposes.
# It is also provided as a convenience to those who want to deploy these URLs
# elsewhere.

from django.contrib import admin
from django.conf.urls import patterns, url, include

urlpatterns = patterns('djara.django.contrib.admin.views',

    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^(?P<app_label>\w+)/$', admin.site.index, name='app_list'),
    url(r'^jsi18n/$', admin.site.i18n_javascript, name='jsi18n'),
    url(r'^$', admin.site.index, name='index'),
    # url(r'^password_change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    # url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    # url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    # url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    # # Support old style base36 password reset links; remove in Django 1.7
    # url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     'django.contrib.auth.views.password_reset_confirm_uidb36'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     'django.contrib.auth.views.password_reset_confirm',
    #     name='password_reset_confirm'),
    # url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
)

# Add the real url patterns of the admin
urlpatterns += admin.site.get_urls()