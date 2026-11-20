from django.urls import path
from . import views, cloud_api
urlpatterns=[
    path('api/config/', cloud_api.api_config, name='api_config'),
    path('api/health/', cloud_api.api_health, name='api_health'),
    path('api/journals/', cloud_api.journals, name='api_journals'),
    path('api/journals/<uuid:entry_id>/', cloud_api.delete_journal, name='api_journal_delete'),
    path('api/checkins/', cloud_api.checkins, name='api_checkins'),
    path('api/checkins/<uuid:entry_id>/', cloud_api.delete_checkin, name='api_checkin_delete'),
    path('api/my-data/', cloud_api.delete_all, name='api_delete_data'),
    path('',views.home,name='home'),path('demo/',views.demo,name='demo'),
    path('health/',views.health,name='health'),
    path('signup/',views.signup,name='signup'),
    path('accounts/login/',views.signin,name='login'),
    path('accounts/logout/',views.signout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('assessment/',views.assessment_view,name='assessment'),
    path('result/<int:response_id>/',views.result_view,name='result'),
    path('journal/',views.journal_entry,name='journal'),
    path('journal/<int:entry_id>/delete/',views.journal_delete,name='journal_delete'),
    path('chatbot/',views.chatbot_view,name='chatbot'),
]
