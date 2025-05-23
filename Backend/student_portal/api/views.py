from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Student, ActivityLog, Marks
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView

# Admin-only: Create a new student and send email

@api_view(['POST'])
@permission_classes([])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'detail': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token, created = Token.objects.get_or_create(user=user)

    # Determine role
    is_admin = user.is_staff or user.is_superuser
    is_student = Student.objects.filter(user=user).exists()
    
    return Response({
        'token': token.key,
        'is_admin': is_admin,
        'is_student': is_student,
        'username': user.username,
    })


class CreateStudentView(generics.CreateAPIView):
    serializer_class = CreateStudentSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        student = serializer.save()

        send_mail(
            subject='Your Student Portal Login',
            message=(
                f"Hello {student.user.first_name},\n\n"
                f"Your student account has been created.\n"
                f"Username: {student.user.username}\n"
                f"Please use the password you were given to log in.\n\n"
                "Log in to your dashboard to check your progress.\n\n"
                "Best regards,\nStudent Portal Team"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[student.user.email],
            fail_silently=False,
        )

# Admin-only: List all students
class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminUser]

# Admin-only: Mark a student as having completed their degree
class MarkDegreeCompletedView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        student = self.get_object()
        student.degree_completed = True
        student.save()
        ActivityLog.objects.create(student=student, action="Degree marked as completed")

        send_mail(
            'Degree Completed!',
            'Congratulations! Your degree is marked as completed. Check your portal to download the certificate.',
            settings.EMAIL_HOST_USER,
            [student.user.email],
            fail_silently=False,
        )
        return Response({"message": "Marked as completed"}, status=200)

# Admin-only: Upload a certificate for the student
class UploadCertificateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        student = self.get_object()
        certificate = request.FILES.get('certificate')
        if certificate:
            student.certificate = certificate
            student.save()
            return Response({"message": "Certificate uploaded."})
        return Response({"error": "No file provided"}, status=400)

# Student-only: View their own profile and progress
class StudentDashboardView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Student.objects.get(user=self.request.user)

# Admin-only: Upload marks for a student
class UploadMarksView(generics.CreateAPIView):
    serializer_class = MarksSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        marks = serializer.save()
        ActivityLog.objects.create(student=marks.student, action=f"Marks uploaded for {marks.subject}: {marks.score}")

# Student-only: View their own marks summary
class MarksSummaryView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Marks.objects.filter(student__user=self.request.user)
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer