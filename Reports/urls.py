from django.conf.urls import url
from Reports import views

urlpatterns = [

    # landing pages
    url(r'^$', views.landing_page_view, name='Landing Page'),
    url(r'^home$', views.home, name='Home'),
    url(r'^schedule_demo$', views.schedule_demo, name='Schedule demo'),

    # parent pages
    url(r'^day', views.day_view, name='day'),

    # teacher logging pages
    url(r'^log$', views.log_drc_view, name='log daily reports'),
    url(r'^log/([0-9_-]{9,11})', views.log_past_drc_view, name='log past reports'),

    # data representation pages
    url(r'^weekly_view/([a-zA-z0-9_-]{3,16})', views.raw_week_view, name='view week'),
    url(r'^graph/([a-zA-z0-9_-]{3,16})/([0-9_-]{9,11})/to/([0-9_-]{9,11})$', views.graph_view, name='view graph'),
    url(r'^insights/([a-zA-z0-9_-]{3,16})', views.insights_view, name='view insights'),

    # principal only pages
    url(r'TeacherSubmissions', views.track_reports_view, name='view teacher submission stats'),

    # helper pages
    url(r'^current_wr_redirect/([a-zA-z0-9_-]{3,16})$', views.current_week_redirect, name='week redirect'),
    url(r'^home', views.home, name='home'),
]

