from django.urls import path
from . import views

urlpatterns = [
    path('api/word-of-day/', views.get_word_of_day, name='word_of_day'),
    path('api/stats/', views.get_user_stats, name='user_stats'),
    path('api/sync/', views.sync_local_words, name='sync_local_words'),
    path('api/word/<str:word_text>/', views.get_word_data, name='word_data'),
]