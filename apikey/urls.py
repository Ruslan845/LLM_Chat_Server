# your_app/urls.py
from django.urls import path
from .views import get_all, set_key

urlpatterns = [
    path('get_all/', get_all, name='get_all'),
    path('set_key/', set_key, name='set_key'),
]