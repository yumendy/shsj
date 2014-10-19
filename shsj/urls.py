from django.conf.urls import patterns, include, url
from django.contrib import admin
from volunteer import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shsj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^djangoadmin/', include(admin.site.urls)),
    url(r'^$', views.homepage),
    url(r'^signup/$', views.signup),
    url(r'^login/$',views.login),
    url(r'^logout/$',views.logout),
    url(r'^submitreport/$',views.submitreport),
    url(r'^reportlist/$',views.report_list),
    url(r'^reportlist/edit/$',views.report_edit),
    url(r'^reportlist/detail/$',views.report_detail),
    url(r'^auditinglist/$',views.auditing_list),
)
