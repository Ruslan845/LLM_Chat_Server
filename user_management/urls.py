from django.urls import path, re_path
from .views import get_one_user, get_all_users, update_user, delete_user

urlpatterns = [
    path('getoneuser/<str:user_id>/', get_one_user, name='get_one_user'),
    path('getallusers/', get_all_users, name='get_all_users'),
    path('updateuser/<str:user_id>/', update_user, name='update_user'),
    re_path(r'^updateuser/(?P<user_id>[^/]+)$', update_user),  # Handle URLs without trailing slash
    path('deleteuser/<str:user_id>/', delete_user, name='delete_user'),
]