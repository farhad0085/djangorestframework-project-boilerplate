from django.urls import path
from .views import *


urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('register/', RegisterAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('user/me/', UserInfoAPIView.as_view()),
    path('password/change/', PasswordChangeView.as_view()),
    path('password/reset/', PasswordResetAPIView.as_view()),
    path('password/reset/confirm/', PasswordResetConfirmAPIView.as_view()),
]
