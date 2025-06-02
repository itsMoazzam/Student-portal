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
    path("categories/", manage_categories, name="manage-categories"),
    path("students/<int:pk>/categorize/", categorize_student, name="categorize-student"),

    path('students/', StudentListView.as_view()),
    path('students/create/', CreateStudentView.as_view()),
    path('students/<int:pk>/complete/', MarkDegreeCompletedView.as_view()),
    path('students/<int:pk>/upload-certificate/', UploadCertificateView.as_view()),
    path('dashboard/', StudentDashboardView.as_view()),
     path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('profile/', StudentProfileRetrieveUpdateView.as_view(), name='student-profile'),
    path('profile/request-approval/', StudentProfileApprovalView.as_view(), name='request-approval'),
]
