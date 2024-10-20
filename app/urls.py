from django.urls import path
from . import views
from .views import upload

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', upload, name='upload'),
]