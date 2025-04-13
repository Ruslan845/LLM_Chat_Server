from django.urls import path, re_path
from .views import ask_gpt, add_chat, get_chat, get_title_list

urlpatterns = [
    # path('getoneuser/<str:user_id>/', get_one_user, name='get_one_user'),
    path('addchat/', add_chat, name='add_chat'),
    path('getchat/', get_chat, name='get_chat'),
    path('gettitlelist/', get_title_list, name='get_title_list'),
    # re_path(r'^openai/(?P<chat_number>[^/]+)$', ask_gpt),  # Handle URLs without trailing slas
    path('askgpt/', ask_gpt, name='ask_gpt'),
]