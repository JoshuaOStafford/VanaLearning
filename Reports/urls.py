from django.conf.urls import url
from Reports import views

urlpatterns = [
    url(r'^$', views.landing_page_view, name='Landing Page'),
    url(r'^schedule_demo$', views.schedule_demo, name='schedule_demo'),
    url(r'^home', views.user_home, name='user_home'),
    url(r'^log/DailyReports', views.log_drc_view, name='log daily reports'),
    url(r'^log/PastReports', views.log_drc_view, name='log daily reports'),
    url(r'^edit/DailyReport/([a-zA-z0-9_-]{3,16})', views.edit_drc_view, name='edit daily report'),
    url(r'^PastSubmissions/([a-zA-z0-9_-]{3,16})', views.past_submissions_view, name='view past submissions'),
    url(r'^StudentHistory/([a-zA-z0-9_-]{3,16})', views.student_history_view, name='student history'),
    url(r'^ProgressGraph/([a-zA-z0-9_-]{3,16})/([0-9_-]{9,11})/to/([0-9_-]{9,11})$', views.progress_graph_view,
        name='progress graph'),
    url(r'^WeeklyReports/([a-zA-z0-9_-]{3,16})', views.weekly_reports_view, name='view weekly reports'),
    url(r'TeacherSubmissions', views.teacher_submissions_view, name='view teacher submission stats'),
    url(r'^current_wr_redirect/([a-zA-z0-9_-]{3,16})$', views.current_week_report_redirect, name='WR_redirect'),
]

