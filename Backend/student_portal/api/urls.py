from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login_view, name='login'),

    path('students/', StudentListView.as_view()),
    path('students/create/', CreateStudentView.as_view()),
    path('students/<int:pk>/complete/', MarkDegreeCompletedView.as_view()),
    path('students/<int:pk>/upload-certificate/', UploadCertificateView.as_view()),
    path('dashboard/', StudentDashboardView.as_view()),
]
