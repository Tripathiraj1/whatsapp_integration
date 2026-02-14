from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('chat/', views.chat_with_gpt, name='chat_with_gpt'),
]
