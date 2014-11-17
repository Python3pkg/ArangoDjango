from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns

###############
## I18N URLS ##
###############
urlpatterns = patterns('djara.django.auth.views',

    # Login
    url(r'^login/$', view='login_view', name='login-view'),
    url(r'^login/action/(?P<view_name>[a-z|A-Z]+[:][a-z|A-Z]+)/$', view='login_action', name='login-action'),

    # Logout
    url(r'^logout/action/(?P<view_name>[a-z|A-Z]+[:][a-z|A-Z]+)/$', view='logout_action', name='logout-action'),

    # Register
    url(r'^register/$', view='register_view', name='register-view'),
    url(r'^register/action/(?P<view_name>[a-z|A-Z]+[:][a-z|A-Z]+)/$', view='register_action', name='register-action'),
    url(r'^register/activate/(?P<activation_key>.+)/(?P<uuid>.+)/(?P<view_name>[a-z|A-Z]+[:][a-z|A-Z]+)/$', view='register_activate', name='register-activate'),
)
