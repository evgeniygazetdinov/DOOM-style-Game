from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('info/', views.info, name='info'),
    path('latency/', views.latency, name='latency'),
    path('logout/', views.logout, name='logout'),
]