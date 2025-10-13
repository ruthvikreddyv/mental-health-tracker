from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('assessment/', views.assessment_view, name='assessment'),
    path('result/<int:score>/', views.result_view, name='result'),
    path('signup/', views.signup, name='signup'),
    path('journal/', views.journal_entry, name='journal'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chatbot/', views.chatbot_view, name='chatbot'),

]

