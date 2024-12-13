from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', views.UserRegistrationAPIView.as_view(), name='user-register'),
    path('activate/<uidb64>/<token>/', views.ActivateAPIView.as_view(), name='activate-api'),
    path('reset-password/', views.PasswordResetRequestAPIView.as_view(), name='reset-password'),
    path('set-password/<uidb64>/<token>/', views.PasswordResetConfirmAPIView.as_view(), name='set-password'),
]
