# your_app/urls.py
from django.urls import path
from .views import google_auth_view, linkedin_auth_view, facebook_auth_view, set_csrf_cookie, refresh_token

urlpatterns = [
    path('google/', google_auth_view, name='google_auth'),
    path('linkedin/', linkedin_auth_view, name='linkedin_auth'),
    path('facebook/', facebook_auth_view, name='facebook_auth'),
    path('set-csrf-cookie/', set_csrf_cookie, name='set_csrf_cookie'),
    path('refresh-token/', refresh_token, name='refresh_token'),
]