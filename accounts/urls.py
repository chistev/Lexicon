from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/status/', views.newsletter_status, name='newsletter_status'),
    path('newsletter/confirm/<str:token>/', views.confirm_newsletter, name='confirm_newsletter'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('newsletter/unsubscribe/<str:email>/', views.newsletter_unsubscribe_by_email, name='unsubscribe_by_email'),
]