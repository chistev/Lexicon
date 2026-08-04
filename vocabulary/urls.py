from django.urls import path
from . import views

urlpatterns = [
    path('api/word-of-day/', views.get_word_of_day, name='word_of_day'),
]