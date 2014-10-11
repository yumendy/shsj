from django.conf.urls import patterns, include, url
from django.contrib import admin
from volunteer import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shsj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^djangoadmin/', include(admin.site.urls)),
    url(r'^$', views.homepage),
)
