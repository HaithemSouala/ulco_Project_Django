from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', RedirectView.as_view(url='/recipes/')),
                           url(r'^recipes/', include('recipes.urls')),
                           url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
                           url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login',name='logout'),
                           url(r'^admin/', include(admin.site.urls)),
                       )