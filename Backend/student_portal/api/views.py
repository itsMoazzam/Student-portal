from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Student, ActivityLog, Marks, TaskSubmission
from .serializers import *
# from .serializers import TaskSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsStudent
import csv
from io import TextIOWrapper
from reportlab.pdfgen import canvas
from django.http import HttpResponse
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
        # Extract raw password from validated data
        raw_password = self.request.data.get('password')
        user = serializer.save()  # serializer should already create a User and Student

        # Set password properly (secure hashing)
        user.set_password(raw_password)
        user.save()

        # Send email
        try:
            send_mail(
                subject='Your Student Portal Login',
                message=(
                    f"Hello {user.first_name or user.username},\n\n"
                    f"Your student account has been created.\n"
                    f"Username: {user.username}\n"
                    f"Password: {raw_password}\n\n"
                    "Please log in to your dashboard to check your progress.\n\n"
                    "Best regards,\nStudent Portal Team"
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'error': f'User created but failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message': 'Student created and email sent.'}, status=status.HTTP_201_CREATED)

        
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

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def bulk_add_students(request):
    csv_file = request.FILES.get("file")
    if not csv_file:
        return Response({"error": "No file uploaded."}, status=400)

    reader = csv.DictReader(TextIOWrapper(csv_file, encoding='utf-8'))
    created_users = []

    for row in reader:
        username = row.get('username')
        email = row.get('email')
        password = User.objects.make_random_password()

        if User.objects.filter(username=username).exists():
            continue

        user = User.objects.create_user(username=username, email=email, password=password)
        Student.objects.create(user=user)
        created_users.append(username)

        send_mail(
            subject="Student Account Created",
            message=f"Username: {username}\nPassword: {password}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

    return Response({"created": created_users}, status=201)

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def categorize_student(request, pk):
    category = request.data.get('category')
    student = Student.objects.get(pk=pk)
    student.category = category
    student.save()
    return Response({"message": "Category assigned."})

class AssignTaskView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def review_submission(request, submission_id):
    submission = TaskSubmission.objects.get(id=submission_id)
    status = request.data.get('review_status')
    submission.review_status = status
    submission.save()
    return Response({"message": "Review updated."})


# Student-only: View their own profile and progress
class StudentDashboardView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsStudent]

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
    
    
    
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def generate_pdf_report(request, student_id):
    student = Student.objects.get(id=student_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.user.username}_report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Report for {student.user.username}")
    p.drawString(100, 780, f"Degree Completed: {student.degree_completed}")
    p.drawString(100, 760, f"Category: {student.category or 'N/A'}")
    # Add more info...

    p.showPage()
    p.save()
    return response