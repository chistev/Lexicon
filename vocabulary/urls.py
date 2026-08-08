from django.urls import path
from . import views

urlpatterns = [
    path('api/word-of-day/', views.get_word_of_day, name='word_of_day'),
    path('api/stats/', views.get_user_stats, name='user_stats'),
    path('api/sync/', views.sync_local_words, name='sync_local_words'),
    path('api/word/<str:word_text>/', views.get_word_data, name='word_data'),
    path('api/mark-known/', views.mark_word_known, name='mark_word_known'),
    path('api/review-words/', views.get_review_words, name='review_words'),
    path('api/user-words/', views.get_user_words, name='user_words'),
    path('api/save-word/', views.save_word, name='save_word'),
]